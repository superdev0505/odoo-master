# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class account_invoice(models.Model):
    _inherit = "account.invoice"

    offer_id = fields.Many2one('web.offers', 'Offer')


class account_payment(models.Model):
    _inherit = "account.payment"

    offer_id = fields.Many2one('web.offers', 'Offer')
    biller_customer_id = fields.Char('Biller Customer ID')
    biller_transaction_id = fields.Char('Biller Transaction ID')
    card_type = fields.Char('Card Type')
    card_code = fields.Integer('Card Code')
    biller_data = fields.Text('Biller Data')

    @api.model
    def default_get(self, fields):
        rec = super(account_payment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            if invoice.get('offer_id'):
                rec['offer_id'] = invoice['offer_id'][0]
        return rec

    @api.multi
    def post(self):
        res = super(account_payment, self).post()

        s_obj = self.env['web.api.service']
        m_obj = self.env['met.art']
        for rec in self:

            #sale_ids = []
            #sale_obj = self.env['sale.order']
            #for inv in self.invoice_ids:
            #    for line in inv.invoice_line_ids:
            #        for sl in line.sale_line_ids:
            #            if not sl.order_id.id in sale_ids:
            #                sale_ids.append(sl.order_id.id)

            #HasOffers
            #Getting the affiliate Id
            affiliate_ids = []
            partner_ids = []
            site_ids = []
            for inv in self.invoice_ids:
                if inv.team_id:
                    affiliate_ids.append(inv.team_id.external_id)
                if inv.partner_id:
                    partner_ids.append(inv.partner_id)
                    for line in inv.invoice_line_ids:
                        if line.product_id and line.product_id.product_tmpl_id:
                            if line.product_id.product_tmpl_id.site_subscription:
                                site_ids.append(line.product_id.product_tmpl_id.site_code)
            if not len(affiliate_ids) == 1:
                raise ValidationError(_('This invoice has many affiliate_ids. It must have only one. Please review it'))
            external_affiliate_id = affiliate_ids[0]

            #Getting the offer external_id
            external_offer_id = rec.offer_id.external_id

            sale_amount = rec.amount
            if rec.offer_id.revenue_type == "cpa_percentage":
                revenue = sale_amount * (rec.offer_id.max_percent_payout/100)
            elif rec.offer_id.revenue_type == "cpa_flat":
                revenue = rec.offer_id.max_payout
            elif rec.offer_id.revenue_type == "cpa_both":
                revenue = (sale_amount * (rec.offer_id.max_percent_payout/100)) + rec.offer_id.max_payout
            else:
                raise ValidationError(_('Revenue Not Supported'))

            if rec.offer_id.payout_type == "cpa_percentage":
                payout = sale_amount * (rec.offer_id.percent_payout/100)
            elif rec.offer_id.revenue_type == "cpa_flat":
                payout = rec.offer_id.default_payout
            elif rec.offer_id.revenue_type == "cpa_both":
                payout = (sale_amount * (rec.offer_id.percent_payout/100)) + rec.offer_id.default_payout
            else:
                raise ValidationError(_('Revenue Not Supported'))

            sale_parameters={"Target": "Conversion",
                             "Method": "create",
                             "data[offer_id]": external_offer_id,
                             "data[affiliate_id]": external_affiliate_id,
                             "data[revenue]": revenue,
                             "data[sale_amount]": sale_amount,
                             "data[payout]": payout}

            self.offer_id.offer_service_id.service_id.call_api(context={},dict_parameters=sale_parameters)


            for po in partner_ids:
                if site_ids:
                    m_obj.create_user(po.ma_username, po.ma_password, po.email, 'test','test',localization='us',sites=site_ids)




        return res