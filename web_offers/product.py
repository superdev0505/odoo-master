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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    site_ids = fields.Many2many('crm.site','crm_site_product_rel', 'product_tmpl_id', 'site_id', 'Sites')

    allow_all_affiliates = fields.Boolean('Allow All Affiliates', default=True)
    affiliates_allowed = fields.Many2many('crm.team','product_temaplate_crm_team_rel', 'product_tmpl_id','team_id', 'Affiliates Allowed', domain=[('type','=','affiliate')])

    site_subscription = fields.Boolean('MetArt Subscription')
    site_code = fields.Char('MetArt Code')