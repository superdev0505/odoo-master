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


class CrmSite(models.Model):
    _name = 'crm.site'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'CRM Site'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    url = fields.Char('URL')
    brand_id = fields.Many2one('crm.brand', 'Brand')
    manager_id = fields.Many2one('res.partner', 'Manager')
    team_id = fields.Many2one('crm.team', 'Affiliate')
    state = fields.Selection([('offline', 'Offline'),('online', 'Online')], string='Site State', default="online")

    product_ids = fields.Many2many('product.template', 'crm_site_product_rel', 'site_id', 'product_tmpl_id', 'Products')