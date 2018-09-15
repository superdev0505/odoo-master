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

class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    def _prepare_combo_invoice_line(self, cr, uid, line, fiscal_position, context=None):
        invoice_lines = []
        fpos_obj = self.pool.get('account.fiscal.position')
        res = line.product_id
        account_id = res.property_account_income_id.id
        if not account_id:
            account_id = res.categ_id.property_account_income_categ_id.id
        account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)

        if context.get('force_company'):
            taxes = res.taxes_id.filtered(lambda r: r.company_id.id == context.get('force_company')) or False
        else:
            taxes = res.taxes_id or False

        tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes)
        values = {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': line.analytic_account_id.analytic_account_id.id,
            'price_unit': 0.0,
            'discount': line.discount,
            'quantity': line.quantity,
            'uom_id': line.uom_id.id or False,
            'product_id': line.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, tax_id)],
        }
        invoice_lines.append((0,0,values))

        for p in line.product_id.child_product_combo_ids:
            values = {
                'name': line.name,
                'account_id': account_id,
                'account_analytic_id': line.analytic_account_id.analytic_account_id.id,
                'price_unit': p.price_applied or 0.0,
                'discount': 0.0,
                'quantity': line.quantity,
                'uom_id': line.uom_id.id or False,
                'product_id': p.product_id.product_variant_ids[0].id,
                'invoice_line_tax_ids': [(6, 0, tax_id)],
            }
            invoice_lines.append((0, 0, values))

        return invoice_lines

    def _prepare_invoice_lines(self, cr, uid, contract, fiscal_position_id, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        fiscal_position = None
        if fiscal_position_id:
            fiscal_position = fpos_obj.browse(cr, uid, fiscal_position_id, context=context)
        invoice_lines = []
        for line in contract.recurring_invoice_line_ids:
            if line.product_id.is_combo:
                combo_lines = self._prepare_combo_invoice_line(cr, uid, line, fiscal_position, context=context)
                invoice_lines = invoice_lines + combo_lines
            else:
                values = self._prepare_invoice_line(cr, uid, line, fiscal_position, context=context)
                invoice_lines.append((0, 0, values))
        return invoice_lines