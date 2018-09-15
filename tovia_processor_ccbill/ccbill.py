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

class CCBillProcessor(models.Model):

    _name = 'ccbill.data'
    _description = 'CCbill Data'

    subaccount = fields.Char('SubAccount')
    subaccount_url = fields.Char('SubAccount URL')
    site_name = fields.Char('Site Name')
    site_active = fields.Boolean('Active')
    description = fields.Char('Description')
    copy = fields.Char('Copy')
    main = fields.Char('Main')
    split_to_us = fields.Integer('Split to Us')
    notes = fields.Text('Notes')