# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import expression
from openerp import tools

from openerp import models, fields, api, _, tools
from lxml import etree


class ToviaInvoiceReport(models.Model):
    _name = 'tovia.invoice.report'
    _description = 'Tovia Invoice Report'
    _auto = False

    team_id = fields.Many2one('crm.team', string='Affiliate')
    product_type = fields.Selection([('internal', 'Internal'),
                                     ('external', 'External')], string='Product Type', default='internal')
    product_id = fields.Many2one('product.product', string='Product')
    subscription_product = fields.Boolean(string='Subscription Product')
    date = fields.Date(string='Date Invoice')
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    price_total = fields.Float(string='Total')
    partner_id = fields.Many2one('res.partner', string='Customer')
    discount = fields.Float(string='Discount')
    quantity = fields.Float(string='Product Quantity')
    type = fields.Selection([('consu', _('Consumable')),
                             ('service', _('Service')),
                             ('product', _('Stockable Product')),
                             ('digital', _('Digital Content'))], string='Type')
    country_id = fields.Many2one('res.country', string='Country')

    def _select(self):
        select_str = """
    SELECT
    ai.team_id,
	pt.product_type,
	ail.product_id,
	coalesce(pt.recurring_invoice, false) as subscription_product,
	ai.date_invoice as date,
	pt.categ_id,
	ail.price_subtotal as price_total,
	ai.partner_id,
	ail.discount,
	ail.quantity,
	pt.type,
	rp.country_id
FROM account_invoice_line ail
LEFT JOIN account_invoice ai
	ON ai.id = ail.invoice_id
LEFT JOIN product_product pp
	ON pp.id = ail.product_id
LEFT JOIN product_template pt
	ON pt.id = pp.product_tmpl_id
LEFT JOIN res_partner rp
    ON rp.id = ai.partner_id
WHERE ai.type = 'out_invoice' AND ai.state = 'paid'
        """
        return select_str

    def init(self, cr):
        # self._table = tovia_invoice_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT row_number() over() as id, *
                FROM ((
                    %s
                )) as rep
        )""" % (self._table, self._select()))