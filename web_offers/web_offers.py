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


class WebApiOfferService(models.Model):
    _name = 'web.api.offer.service'
    _description = 'Web Api Offer Services'

    name = fields.Char('Name')
    service_id = fields.Many2one('web.api.service', 'Service')

    min_refresh_interval = fields.Integer('Minimum time of interval to refresh it again', default=30)
    last_refresh = fields.Datetime('Last Refresh')

    parameters = fields.One2many('web.api.offer.service.parameter', 'service_id', 'Parameters',
                                 help='Parameters to be added on offer request')
    offers = fields.One2many('web.offers', 'offer_service_id', 'Offers')
    offers_path = fields.Text('Offers Path')
    offers_external_id = fields.Char('Offer External Id')
    offers_name = fields.Char('Offer Name')

    request_data = fields.One2many('web.api.offer.service.request.data', 'service_id', 'Request Data')

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
            res.append({'data': {'external_id': d.get(eid_key),
                                 'name': d.get(name_key),
                                 'offer_service_id': sid},
                        'full_data': d})

        return res


    def compare_offers(self, cr, uid, web_offers, db_offers):

        web_eids = []
        db_eids = []
        for w in web_offers:
            web_eids.append(w.get('data').get('external_id'))
        for d in db_offers:
            db_eids.append(d.get('external_id'))

        eids_to_del = [x for x in db_eids if x not in web_eids]
        eids_to_create = [x for x in web_eids if x not in db_eids]
        eids_to_update = [x for x in web_eids if x in db_eids]

        return eids_to_create, eids_to_update, eids_to_del

    def sync_offers(self, cr, uid, ids=None, context={}):
        s_obj = self.pool.get('web.api.service')
        o_obj = self.pool.get('web.offers')

        if context is None:
            context = {}
        else:
            context = dict(context or {})

        if not ids:
            ids = self.search(cr, uid, [])

        context.update({'no_refresh': True})

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
            offers = self.find_by_path(s.offers_path, json_r, s.offers_external_id, s.offers_name, s.id)
            actual_offers_ids = o_obj.search(cr, uid, [('offer_service_id', '=', s.id)], context=context)
            actual_offers = o_obj.read(cr, uid, actual_offers_ids, fields=['external_id', 'name'], context=context)

            tc, tu, td = self.compare_offers(cr, uid, offers, actual_offers)

            for o in offers:
                w_ids = False
                if o['data']['external_id'] in tc:
                    w_ids = o_obj.create(cr, SUPERUSER_ID, o['data'])
                elif o['data']['external_id'] in tu:
                    w_ids = o_obj.search(cr, SUPERUSER_ID, ['&',('external_id','=',o['data']['external_id']),('offer_service_id','=',s.id)])
                    o_obj.write(cr, SUPERUSER_ID, w_ids, o['data'])

                data_to_write = {}

                for r in s.request_data:
                    data_to_write[r.field_name] = o['full_data'].get(r.name, None)

                if data_to_write:
                    if isinstance(w_ids, (int, long)):
                        w_ids = [w_ids]
                    o_obj.write(cr, SUPERUSER_ID, w_ids, data_to_write)

            if td:
                wd_ids = o_obj.search(cr, SUPERUSER_ID,
                                     ['&', ('external_id', 'in', td), ('offer_service_id', '=', s.id)])
                o_obj.unlink(cr, SUPERUSER_ID, wd_ids)



        return True


class WebApiOfferServiceParameters(models.Model):
    _name = 'web.api.offer.service.parameter'
    _inherit = 'web.api.service.parameter'
    _description = 'Web Api Offer Service Parameters'

    service_id = fields.Many2one('web.api.offer.service', 'Web Offer Service')


class WebApiOfferServiceRequestData(models.Model):
    _name = 'web.api.offer.service.request.data'
    _inherit = 'web.api.service.request.data'
    _description = 'Web Api Offer Service Request Data'

    service_id = fields.Many2one('web.api.offer.service', 'Web Offer Service')


class WebOffers(models.Model):
    _name = 'web.offers'
    _description = 'Web Offers'

    name = fields.Char('Name')
    external_id = fields.Char('External ID')
    offer_service_id = fields.Many2one('web.api.offer.service', 'Offer Service')

    #HasOffers
    max_payout = fields.Float('Max Payout')
    max_percent_payout = fields.Float('Max Percent Payout')
    revenue_type = fields.Selection([('cpa_flat','Revenue per Conversion (RPA)'),
                                     ('cpa_percentage','Revenue per Sale (RPS)'),
                                     ('cpa_both','Revenue per Conversion plus Revenue per Sale (RPA + RPS)'),
                                     ('cpc','Revenue per Click (RPC)'),
                                     ('cpm','Revenue per Thousand Impressions (RPM)')], string='Revenue Type')

    payout_type = fields.Selection([('cpa_flat','Cost per Conversion (CPA)'),
                                    ('cpa_percentage', 'Cost per Sale (CPS)'),
                                    ('cpa_both', 'Cost per Conversion plus Cost per Sale (CPA + CPS)'),
                                    ('cpc', 'Cost per Click (CPC)'),
                                    ('cpm', 'Cost per Thousand Impressions (CPM)')], string='Payout Type')

    default_payout = fields.Float('Default Payout')
    percent_payout = fields.Float('Percent Payout')



    _sql_constraints = [
        ('web_offers_uniq', 'unique(external_id, offer_service_id)', 'Offers per service must be unique !'),
    ]

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(WebOffers, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        os_obj = self.env['web.api.offer.service']
        os_ids = os_obj.search([])
        os_ids.sync_offers()
        return result