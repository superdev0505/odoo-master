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

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import UserError, RedirectWarning, ValidationError

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.model
    def _get_default_team(self):
        default_team_id = self.env['crm.team']._get_default_team_id()
        return self.env['crm.team'].browse(default_team_id)

    offer_id = fields.Many2one('web.offers', 'Offer')
    team_id = fields.Many2one('crm.team', 'Affiliate', change_default=True, default=_get_default_team,
                              oldname='section_id')

    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for sub in self.browse(cr, uid, ids, context=context):
            if sub.type != 'template':
                name = '%s - %s' % (sub.code, sub.partner_id.name) if sub.code else sub.partner_id.name
                if sub.template_id:
                    res.append((sub.id, '%s/%s' % (sub.template_id.code, name) if sub.template_id.code else name))
                else:
                    res.append((sub.id, name))
            else:
                name = '%s - %s' % (sub.code, sub.name) if sub.code else sub.name
                res.append((sub.id, name))
        return res

    @api.multi
    @api.onchange('team_id')
    def onchange_team_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment term
        - Invoice address
        - Delivery address
        """
        values = {
        }
        if self.team_id:
            if self.team_id.pricelist_id:
                values['pricelist_id'] = self.team_id.pricelist_id.id
            else:
                values['pricelist_id'] = False
        self.update(values)

    @api.cr_uid_ids
    def validate_subscription(self, cr, uid, ids, context={}):
        subscriptions_to_invoice = []

        inv_obj = self.pool.get('account.invoice')
        pay_obj = self.pool.get('account.payment')
        for subscription in self.browse(cr, uid, ids):
            if subscription.state not in ('draft'):
                raise ValidationError(
                    _('The subscription must be on draft to validate it. Use rebill_subscription instead.'))
            for line in subscription.recurring_invoice_line_ids:
                if not line.product_id.recurring_invoice:
                    raise ValidationError(
                        _('The subscription needs a subscription product. Please check it'))

            subscription.set_open()
            subscriptions_to_invoice.append(subscription.id)

        invoice_ids = self.recurring_invoice(cr, uid, subscriptions_to_invoice)
        if invoice_ids:
            if isinstance(invoice_ids, list):
                invoice_id = invoice_ids[0]
            else:
                invoice_id = invoice_ids
            invoice = inv_obj.browse(cr, uid, invoice_id)
            invoice.signal_workflow('invoice_open')
            if context.get('biller_name'):
                journal_obj = self.pool.get('account.journal')
                journal_ids = journal_obj.search(cr, uid, [('name', 'ilike', context.get('biller_name'))])
                if journal_ids:
                    journal_id = journal_obj.browse(cr, uid, journal_ids)
                    payment_type = 'inbound'
                    payment_methods = journal_id.inbound_payment_method_ids
                    payment_method_id = payment_methods and payment_methods[0] or False
                    payment_data = {'journal_id': journal_id.id,
                                    'payment_type': payment_type,
                                    'payment_method_id': payment_method_id.id,
                                    'amount': invoice.residual}
                    if context.get('biller_customer_id'):
                        payment_data['biller_customer_id'] = context.get('biller_customer_id', '')
                    if context.get('biller_transaction_id'):
                        payment_data['biller_transaction_id'] = context.get('biller_transaction_id', '')
                    if context.get('card_type'):
                        payment_data['card_type'] = context.get('card_type', '')
                    if context.get('card_code'):
                        payment_data['card_code'] = context.get('card_code', '')
                    if context.get('biller_data'):
                        payment_data['biller_data'] = context.get('biller_data', '')

                    pay_id = pay_obj.create(cr, uid, payment_data,
                                            context={'default_invoice_ids': [(4, invoice_id, None)]})

                    pay_obj.browse(cr, uid, pay_id).post()
                else:
                    raise ValidationError(_('The biller sent does not exist'))
            else:
                raise ValidationError(_('There is no biller on the dict'))
        return True

    @api.cr_uid_ids
    def rebill_subscription(self, cr, uid, ids, context={}):
        subscriptions_to_invoice = []

        inv_obj = self.pool.get('account.invoice')
        pay_obj = self.pool.get('account.payment')
        for subscription in self.browse(cr, uid, ids):
            if subscription.state not in ('open', 'pending'):
                raise ValidationError(
                    _('The subscription must be a valid subscription.'))
            subscriptions_to_invoice.append(subscription.id)

        invoice_ids = self.recurring_invoice(cr, uid, subscriptions_to_invoice)
        if invoice_ids:
            if isinstance(invoice_ids, list):
                invoice_id = invoice_ids[0]
            else:
                invoice_id = invoice_ids
            invoice = inv_obj.browse(cr, uid, invoice_id)
            invoice.signal_workflow('invoice_open')
            if context.get('biller_name'):
                journal_obj = self.pool.get('account.journal')
                journal_ids = journal_obj.search(cr, uid, [('name', 'ilike', context.get('biller_name'))])
                if journal_ids:
                    journal_id = journal_obj.browse(cr, uid, journal_ids)
                    payment_type = 'inbound'
                    payment_methods = journal_id.inbound_payment_method_ids
                    payment_method_id = payment_methods and payment_methods[0] or False
                    payment_data = {'journal_id': journal_id.id,
                                    'payment_type': payment_type,
                                    'payment_method_id': payment_method_id.id,
                                    'amount': invoice.residual}
                    if context.get('biller_customer_id'):
                        payment_data['biller_customer_id'] = context.get('biller_customer_id', '')
                    if context.get('biller_transaction_id'):
                        payment_data['biller_transaction_id'] = context.get('biller_transaction_id', '')
                    if context.get('card_type'):
                        payment_data['card_type'] = context.get('card_type', '')
                    if context.get('card_code'):
                        payment_data['card_code'] = context.get('card_code', '')
                    if context.get('biller_data'):
                        payment_data['biller_data'] = context.get('biller_data', '')

                    pay_id = pay_obj.create(cr, uid, payment_data,
                                            context={'default_invoice_ids': [(4, invoice_id, None)]})

                    pay_obj.browse(cr, uid, pay_id).post()
                else:
                    raise ValidationError(_('The biller sent does not exist'))
            else:
                raise ValidationError(_('There is no biller on the dict'))

        return True

    def _prepare_invoice_data(self, cr, uid, contract, context=None):
        res = super(SaleSubscription, self)._prepare_invoice_data(cr, uid, contract, context=context)
        res.update({'offer_id': contract.offer_id.id or False, 'team_id': contract.team_id.id or False})
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_default_team(self):
        default_team_id = self.env['crm.team']._get_default_team_id()
        return self.env['crm.team'].browse(default_team_id)

    offer_id = fields.Many2one('web.offers', 'Offer')
    team_id = fields.Many2one('crm.team', 'Affiliate', change_default=True, default=_get_default_team,
                                  oldname='section_id')

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment term
        - Invoice address
        - Delivery address
        """
        super(SaleOrder,self).onchange_partner_id()

        values = {
        }
        if self.team_id:
            if self.team_id.pricelist_id:
                values['pricelist_id'] = self.team_id.pricelist_id.id
            else:
                values['pricelist_id'] = False
        self.update(values)

    @api.multi
    @api.onchange('team_id')
    def onchange_team_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment term
        - Invoice address
        - Delivery address
        """
        values = {
        }
        if self.team_id:
            if self.team_id.pricelist_id:
                values['pricelist_id'] = self.team_id.pricelist_id.id
            else:
                values['pricelist_id'] = False
        self.update(values)

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        res = super(SaleOrder, self).action_invoice_create(grouped=grouped, final=final)
        for order in self:
            inv_obj.browse(res).write({'offer_id': order.offer_id.id})
        return res

    @api.cr_uid_ids
    def validate_quotation(self, cr, uid, ids, context={}):
        orders_to_invoice = []

        inv_obj = self.pool.get('account.invoice')
        pay_obj = self.pool.get('account.payment')
        for order in self.browse(cr, uid, ids):
            if order.state not in ('draft','sent'):
                raise ValidationError(_('The order must be a quotation to be able to validate it. Use revalidate_quotation instead.'))
            for line in order.order_line:
                if line.product_id.type in ('consu','product'):
                    raise ValidationError(
                        _('The order has a stockable product. Please check it'))
            order.action_confirm()
            orders_to_invoice.append(order.id)
        invoice_ids = self.action_invoice_create(cr, uid, orders_to_invoice, final=True)
        if invoice_ids:
            if isinstance(invoice_ids, list):
                invoice_id = invoice_ids[0]
            else:
                invoice_id = invoice_ids
            invoice = inv_obj.browse(cr, uid, invoice_id)
            invoice.signal_workflow('invoice_open')
            if context.get('biller_name'):
                journal_obj = self.pool.get('account.journal')
                journal_ids = journal_obj.search(cr, uid, [('name','ilike',context.get('biller_name'))])
                if journal_ids:
                    journal_id = journal_obj.browse(cr, uid, journal_ids)
                    payment_type = 'inbound'
                    payment_methods = journal_id.inbound_payment_method_ids
                    payment_method_id = payment_methods and payment_methods[0] or False
                    payment_data = {'journal_id': journal_id.id,
                                    'payment_type': payment_type,
                                    'payment_method_id': payment_method_id.id,
                                    'amount': invoice.residual,
                                    'biller_customer_id': context.get('biller_customer_id', ''),
                                    'biller_transaction_id': context.get('biller_transaction_id', ''),
                                    'card_code': context.get('card_code', ''),
                                    'biller_data': context.get('biller_data', ''),
                                    }

                    pay_id = pay_obj.create(cr, uid, payment_data, context={'default_invoice_ids': [(4, invoice_id, None)]})

                    pay_obj.browse(cr, uid, pay_id).post()
                else:
                    raise ValidationError(_('The biller sent does not exist'))
            else:
                raise ValidationError(_('There is no biller on the dict'))

        for order in self.browse(cr, uid, ids):
            order.action_done()
        return True

    @api.cr_uid_ids
    def rebill_quotation(self, cr, uid, ids, context={}):
        new_quotations = []
        for order in self.browse(cr, uid, ids):
            new_id = order.copy()
            new_quotations.append(new_id)
        self.validate_quotation(cr, uid, ids, context=context)

        return new_quotations