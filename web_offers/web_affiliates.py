# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Module
#    Copyright (C) 2015 Grover Menacho (<http://www.grovermenacho.com>).
#    Autor: Grover Menacho
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re
import datetime

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import UserError, RedirectWarning, ValidationError


class WebApiAffiliateService(models.Model):
    _name = 'web.api.affiliate.service'
    _description = 'Web Api Affiliate Services'

    name = fields.Char('Name')
    service_id = fields.Many2one('web.api.service', 'Service')

    min_refresh_interval = fields.Integer('Minimum time of interval to refresh it again', default=30)
    last_refresh = fields.Datetime('Last Refresh')

    parameters = fields.One2many('web.api.affiliate.service.parameter', 'service_id', 'Parameters',
                                 help='Parameters to be added on affiliate request')
    affiliates = fields.One2many('crm.team', 'affiliate_service_id', 'Affiliates')
    affiliates_path = fields.Text('Affiliate Path')
    affiliates_external_id = fields.Char('Affiliate External Id')
    affiliates_name = fields.Char('Affiliate Name')

    def find_by_path(self, path, jdict, eid_key, name_key, sid):
        path_values = re.split(' ', path)
        dicts = [jdict]
        for path_item in path_values:
            filtered = []
            for d in dicts:
                if not isinstance(d, dict):
                    raise ValidationError(
                        _('Path is not well defined. Please check it..'))
                for k, v in d.iteritems():
                    if path_item == "any_value":
                        filtered.append(d[k])
                    else:
                        if k.upper() == path_item.upper():
                            filtered.append(d[k])
            dicts = filtered

        res= []
        for d in dicts:
            res.append({'external_id': d.get(eid_key),
                        'name': d.get(name_key),
                        'affiliate_service_id': sid})

        return res


    def compare_affiliates(self, cr, uid, web_affiliates, db_affiliates):

        web_eids = []
        db_eids = []
        for w in web_affiliates:
            web_eids.append(w.get('external_id'))
        for d in db_affiliates:
            db_eids.append(d.get('external_id'))

        eids_to_del = [x for x in db_eids if x not in web_eids]
        eids_to_create = [x for x in web_eids if x not in db_eids]
        eids_to_update = [x for x in web_eids if x in db_eids]

        return eids_to_create, eids_to_update, eids_to_del

    def sync_affiliates(self, cr, uid, ids=None, context={}):
        s_obj = self.pool.get('web.api.service')
        ct_obj = self.pool.get('crm.team')

        if context is None:
            context = {}
        else:
            context = dict(context or {})

        context.update({'no_refresh': True})

        if not ids:
            ids = self.search(cr, uid, [])

        for s in self.browse(cr, uid, ids):
            if s.last_refresh:
                last_ref = datetime.datetime.strptime(s.last_refresh, "%Y-%m-%d %H:%M:%S")
                diff = datetime.datetime.now() - last_ref
                if diff.total_seconds() < s.min_refresh_interval:
                    continue

            s.write({'last_refresh': datetime.datetime.now()})

            s_parameters = {}

            if s.parameters:
                for p in s.parameters:
                    s_parameters[p.name] = p.value

            json_r = s_obj.call_api(cr, uid, s.service_id.id, dict_parameters=s_parameters)
            affiliates = self.find_by_path(s.affiliates_path, json_r, s.affiliates_external_id, s.affiliates_name, s.id)
            actual_affiliates_ids = ct_obj.search(cr, uid, [('affiliate_service_id', '=', s.id)], context=context)
            actual_affiliates = ct_obj.read(cr, uid, actual_affiliates_ids, fields=['external_id', 'name'], context=context)

            tc, tu, td = self.compare_affiliates(cr, uid, affiliates, actual_affiliates)

            for o in affiliates:
                if o['external_id'] in tc:
                    o.update({'type': 'affiliate'})
                    ct_obj.create(cr, SUPERUSER_ID, o)
                elif o['external_id'] in tu:
                    w_ids = ct_obj.search(cr, SUPERUSER_ID, ['&',('external_id','=',o['external_id']),('affiliate_service_id','=',s.id)])
                    ct_obj.write(cr, SUPERUSER_ID, w_ids, o)
            #We are not going to delete affiliates
            #if td:
            #    wd_ids = ct_obj.search(cr, SUPERUSER_ID,
            #                         ['&', ('external_id', 'in', td), ('affiliate_service_id', '=', s.id)])
            #    ct_obj.unlink(cr, SUPERUSER_ID, wd_ids)


        return True


class WebApiAffiliateServiceParameters(models.Model):
    _name = 'web.api.affiliate.service.parameter'
    _inherit = 'web.api.service.parameter'
    _description = 'Web Api Affiliate Service Parameters'