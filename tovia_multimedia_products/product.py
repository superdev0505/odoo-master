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

class ResMMPhotographer(models.Model):
    _name = 'res.mm.photographer'
    name = fields.Char('Photographer')

class ResMMProducer(models.Model):
    _name = 'res.mm.producer'
    name = fields.Char('Producer')

class ResMMModel(models.Model):
    _name = 'res.mm.model'
    _name = fields.Char('Model')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_mm_type = fields.Selection([('')])

    product_type = fields.Selection([('internal','Internal'),
                                     ('external','External')], string='Product Type', default='internal')
    automatic_supply = fields.Boolean(string='Automatic Supply')
    external_provider = fields.Many2one('res.partner', 'Provider')