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

class EpochProcessor(models.Model):

    _name = 'epoch.data'
    _description = 'Epoch Data'

    site_name = fields.Char('Site')
    description = fields.Char('Description')
    price = fields.Float('Price')
    trial_price = fields.Float('Trial Price')
    pi_code = fields.Char('PI Code')