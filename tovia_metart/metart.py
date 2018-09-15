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
import hashlib
import json
import logging

import time

from openerp import models, fields, api, _, SUPERUSER_ID

_logger = logging.getLogger(__name__)

class MetArt(models.Model):
    _name = 'met.art'

    def generate_headers(self, method, url, partner_key='', request={}):
        """

        :param method: Method should be GET, POST, PUT, DELETE
        :param url: The url where we're going to do the request
        :param partner_key: It's the key to encode
        :param request: It's the dictionary that we're going to send by PUT or POST
        :return:
        """
        timestamp = int(time.time())
        if method not in ('GET','POST','PUT','DELETE'):
            raise Exception
        x_method = method.upper()
        x_url = url
        x_url_lc = x_url.lower()
        x_sk = "0af0722194654fd9ba17b5193e5e06cd" #It's hardcoded right now because we don't have place to this
        if method in ('PUT','POST') and not request:
            raise Exception
        if request:
            x_req = json.dumps(request, ensure_ascii=False)
            m = hashlib.md5()
            md5_to_encode = x_method + ' ' + x_url_lc + ' ' + x_req + ' ' + str(timestamp) + ' ' + x_sk
            m.update(md5_to_encode)
            x_signature = m.hexdigest()
        else:
            m = hashlib.md5()
            md5_to_encode = x_method + ' ' + x_url_lc + ' ' + '' + ' ' + str(timestamp) + ' ' + x_sk
            m.update(md5_to_encode)
            x_signature = m.hexdigest()

        _logger.info("Headers API")
        _logger.info(md5_to_encode)
        _logger.info(x_signature)
        return {
            'X-API-Timestamp': timestamp,
            'X-API-Signature': x_signature
        }

    #OldApi
    def check_username_available(self, cr, uid, username, sites=[]):
        resp = {}
        api_svc = self.pool.get('web.api.service')
        method = 'GET'
        url = "/user/available?username=%s" % username
        sf = False
        for site in sites:
            if not sf:
                url = url + '&site='+site
                sf = True
            else:
                url = url + ','+site

        headers = self.generate_headers(method,url)
        metart_svc_id = api_svc.search(cr, uid, [('service_internal_name', '=', 'metart')])
        if metart_svc_id:
            metart_svc = api_svc.browse(cr, uid, metart_svc_id)
            resp = metart_svc.call_api(dict_headers=headers, alt_url=url, api_method=method)

        return resp

    # OldApi
    @api.cr_uid
    def create_user(self, cr, uid, username, password, email, firstname, lastname, localization='', sites=[], context={}):
        resp = {}
        api_svc = self.pool.get('web.api.service')
        method = 'PUT'
        url = "https://api.met-art.com/user.json"

        x_req = {"user": {"username": username,
                          "password": password,
                          "email": email,
                          "firstName": firstname,
                          "lastName": lastname,
                          "localization": localization,
                          "site": sites}}

        headers = self.generate_headers(method, url, request=x_req)
        metart_svc_id = api_svc.search(cr, uid, [('service_internal_name', '=', 'metart')])
        if metart_svc_id:
            metart_svc = api_svc.browse(cr, uid, metart_svc_id)
            resp = metart_svc.call_api(dict_parameters=x_req, dict_headers=headers, alt_url=url, api_method=method)

        return resp

    # OldApi
    def expire_user(self, cr, uid, username, sites=[]):
        resp = {}
        api_svc = self.pool.get('web.api.service')
        method = 'POST'
        url = "https://api.met-art.com/user.json"

        x_req = {"user": {"username": username,
                          "expired": 1,
                          "site": sites}}

        headers = self.generate_headers(method, url, request=x_req)
        metart_svc_id = api_svc.search(cr, uid, [('service_internal_name', '=', 'metart')])
        if metart_svc_id:
            metart_svc = api_svc.browse(cr, uid, metart_svc_id)
            resp = metart_svc.call_api(dict_parameters=x_req, dict_headers=headers, alt_url=url, api_method=method)

        return resp

    # OldApi
    def enable_expires_user(self, cr, uid, username, sites=[]):
        resp = {}
        api_svc = self.pool.get('web.api.service')
        method = 'POST'
        url = "https://api.met-art.com/user.json"

        x_req = {"user": {"username": username,
                          "expired": 0,
                          "site": sites}}

        headers = self.generate_headers(method, url, request=x_req)
        metart_svc_id = api_svc.search(cr, uid, [('service_internal_name', '=', 'metart')])
        if metart_svc_id:
            metart_svc = api_svc.browse(cr, uid, metart_svc_id)
            resp = metart_svc.call_api(dict_parameters=x_req, dict_headers=headers, alt_url=url, api_method=method)

        return resp



class ResPartner(models.Model):
    _inherit = 'res.partner'
    @api.model
    def old_create(self, vals):
        api_svc = self.env['web.api.service']
        ma_obj = self.env['met.art']
        if vals['name']:
            timestamp = int(time.time())
            #x_method = 'GET'
            #x_url = "https://api.met-art.com/user/available?username=%s" % (vals['name'])
            x_method = 'PUT'
            x_url = "https://api.met-art.com/user.json"
            x_url_lc = x_url.lower()
            x_sk = "0af0722194654fd9ba17b5193e5e06cd"
            x_req = {"user": {"username": "testmauser45678",
                                 "password": "password",
                                 "email": "testemail3@email.com",
                                 "firstName": "Test",
                                 "lastName": "Test",
                                 "localization": "en",
                                 "site": ["MA","SA","EB","EA","TLE"]}}
            #x_req = ''
            m = hashlib.md5()
            md5_to_encode = x_method+' '+x_url_lc+' '+json.dumps(x_req, ensure_ascii=False)+' '+str(timestamp)+' '+x_sk
            m.update(md5_to_encode)
            x_signature = m.hexdigest()
            headers = {'X-API-Timestamp': timestamp,
                       'X-API-Signature': x_signature}
            metart_svc = api_svc.search([('service_internal_name','=','metart')])
            resp = metart_svc.call_api(dict_parameters=x_req,dict_headers=headers, alt_url=x_url, api_method=x_method)

            ma_obj.create_user("testusertovia1","toviatovia","tovia@tovia.com1","Tovia","Tovia",localization="us",sites=["MA"])
        return super(ResPartner, self).create(vals)