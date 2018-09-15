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


_logger = logging.getLogger(__name__)

class ApiServices(models.Model):

    _name = 'web.api.service'
    _description = 'Web API Services'

    name = fields.Char(string='Service Name')
    service_internal_name = fields.Char('Service Internal Name')
    api_url = fields.Char(string='API URL')
    active = fields.Boolean('Active', default=True)
    headers = fields.One2many('web.api.service.header', 'service_id', string='Headers')
    parameters = fields.One2many('web.api.service.parameter', 'service_id', string='Parameters')

    @api.cr_uid_ids
    def call_api(self, cr, uid, service_id, context={}, dict_parameters={}, dict_headers={}, alt_url = '', api_method='GET'):

        if isinstance(service_id, list):
            service_id = service_id[0]

        parameters = {}
        if dict_parameters:
            parameters.update(dict_parameters)
        if service_id:
            service_obj = self.browse(cr, uid, service_id)
            if service_obj.parameters:
                for p in service_obj.parameters:
                    parameters[p.name] = p.value

            api_params = werkzeug.url_encode(parameters)
            if alt_url!='':
                api_url = alt_url
            else:
                api_url = service_obj.api_url

            #url_request = urllib2.Request(api_url, api_params)


            #request.add_header('Accept', 'application/json')
            #request.add_header('Accept-Language', 'en_US')
            #url_request.get_method = lambda: api_method
            headers = {}

            if service_obj.headers:
                for h in service_obj.headers:
                    headers[h.name] = h.value
                    #url_request.add_header(h.name, h.value)

            for k, v in dict_headers.iteritems():
                headers[k] = v
                #url_request.add_header(k, v)
            _logger.info("Calling the API")

            if api_method == 'GET':
                r = requests.get(api_url, params=parameters, headers=headers)
            elif api_method == 'PUT':
                r = requests.put(api_url, json=parameters, headers=headers)
            _logger.info(parameters);

            #url_request = urllib2.urlopen(url_request)
            #result = url_request.read()
            #result_json = json.loads(result)
            #url_request.close()
            result_json = r.json()
            _logger.info(str(result_json))

        return result_json



class ApiServicesParameters(models.Model):

    _name = 'web.api.service.parameter'
    _description = 'Web API Parameters'

    service_id = fields.Many2one('web.api.service', 'Web Service')
    name = fields.Char('Parameter Name')
    description = fields.Char('Description')
    value = fields.Char('Value')

class ApiServicesHeaders(models.Model):

    _name = 'web.api.service.header'
    _description = 'Web API Headers'

    service_id = fields.Many2one('web.api.service', 'Web Service')
    name = fields.Char('Header Name')
    description = fields.Char('Description')
    value = fields.Char('Value')


class ApiServiceRequestData(models.Model):

    _name = 'web.api.service.request.data'
    _description = 'Web API Request Data'

    service_id = fields.Many2one('web.api.service', 'Web Service')
    name = fields.Char('Parameter')
    description = fields.Char('Description')
    field_name = fields.Char('Odoo Field Name')