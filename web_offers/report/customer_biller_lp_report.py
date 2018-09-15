# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import fields, models
from openerp import tools


class customerBillerLpReport(models.Model):
    """ CRM Lead Analysis """
    _name = "customer.biller.lp.report"
    _auto = False
    _description = "Customer Biller Last Payment Report"

    partner_id = fields.Many2one('res.partner', 'Partner')
    biller_name = fields.Char('Biller Name')
    biller_customer_id = fields.Char('Biller Customer ID')
    biller_transaction_id = fields.Char('Biller Transaction ID')
    last_payment_date = fields.Date('Last Payment Date')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'customer_biller_lp_report')
        cr.execute("""
            CREATE OR REPLACE VIEW customer_biller_lp_report AS (
                SELECT DISTINCT ON (ap.partner_id, ap.journal_id) ap.partner_id,
aj.name as biller_name, ap.biller_customer_id, ap.biller_transaction_id, ap.payment_date as last_payment_date, ap.id
FROM account_payment ap
LEFT JOIN account_journal aj
ON aj.id = ap.journal_id
ORDER BY ap.partner_id, ap.journal_id, ap.payment_date desc
            )""")
