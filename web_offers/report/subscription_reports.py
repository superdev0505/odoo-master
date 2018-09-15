# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import fields, models
from openerp import tools

class newSubscriptionsbyMonth(models.Model):
    """ CRM Lead Analysis """
    _name = "subscription.new.month.report"
    _auto = False
    _description = "New subscriptions by month"

    date = fields.Date('Date')
    num = fields.Integer('Subscriptions')

    _order = "date"

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'subscription_new_month_report')
        cr.execute("""
            CREATE OR REPLACE VIEW subscription_new_month_report AS (
SELECT id, date_start as date, 1 as num
FROM sale_subscription
WHERE state not in ('draft')
ORDER BY date_start
            )""")


class EarningsByNewSubscription(models.Model):
    """ CRM Lead Analysis """
    _name = "earnings.new.subscription.report"
    _auto = False
    _description = "Earnings by new subscription report"

    date = fields.Date('Date')
    team_id = fields.Many2one('crm.team', 'Affiliate')
    offer_id = fields.Many2one('web.offers','Offer')
    recurring_total = fields.Float('Recurring Total')

    _order = "date"

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'earnings_new_subscription_report')
        cr.execute("""
            CREATE OR REPLACE VIEW earnings_new_subscription_report AS (
SELECT ss.id, ss.date_start as date, ss.team_id, ss.offer_id, ss.recurring_total
FROM sale_subscription ss
LEFT JOIN account_analytic_account aaa
ON aaa.id = ss.analytic_account_id
WHERE ss.state not in ('draft') AND ss.type = 'contract'
            )""")


class IncomesPerProduct(models.Model):
    """ CRM Lead Analysis """
    _name = "incomes.per.product.report"
    _auto = False
    _description = "Incomes per product report"

    date_invoice = fields.Date('Date')
    product_id = fields.Many2one('product.product', 'Product')
    income = fields.Float('Income')

    _order = "date_invoice"

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'incomes_per_product_report')
        cr.execute("""
            CREATE OR REPLACE VIEW incomes_per_product_report AS (
SELECT ail.id, ai.date_invoice, ail.product_id, ail.price_subtotal as income
FROM account_invoice_line ail
LEFT JOIN account_invoice ai
ON ai.id = ail.invoice_id
LEFT JOIN (
SELECT aaa.id, ss.id as sub_id
FROM sale_subscription ss
LEFT JOIN account_analytic_account aaa
ON aaa.id = ss.analytic_account_id
WHERE ss.state in ('open') AND ss.type = 'contract'
) as a on a.id = ail.account_analytic_id
WHERE ai.state = 'paid'
AND a.sub_id is not null
            )""")
