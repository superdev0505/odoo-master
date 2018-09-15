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


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    type = fields.Selection([('internal','Internal'),('affiliate','Affiliate')], string='Type')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')

    external_id = fields.Char('External ID')
    affiliate_service_id = fields.Many2one('web.api.affiliate.service', 'Offer Service')

    _sql_constraints = [
        ('web_offers_uniq', 'unique(external_id, offer_service_id)', 'Offers per service must be unique !'),
    ]

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(CrmTeam, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        os_obj = self.env['web.api.affiliate.service']
        os_ids = os_obj.search([])
        os_ids.sync_affiliates()
        return result