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

import base64
import json
import logging
import urlparse
import werkzeug.urls
import urllib2

import requests

from openerp import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_combo = fields.Boolean('Is Combo')
    child_product_combo_ids = fields.One2many('product.template.combo','parent_product_id','Combo Products')

class ProductTemplateCombo(models.Model):
    _name = 'product.template.combo'

    parent_product_id = fields.Many2one('product.template','Parent Product')
    product_id = fields.Many2one('product.template', 'Product')
    price_applied = fields.Float('Price Applied')