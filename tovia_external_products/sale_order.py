# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
import datetime

from openerp import api, fields, models
from openerp.tools.translate import _


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    def _get_subscription(self):
        for order in self:
            order.subscription_id = self.env['sale.subscription'].search([('analytic_account_id', '=', order.project_id.id)], limit=1)

    def _search_subscription(self, operator, value):
        if operator not in ['=', '!=', 'in', 'not in']:
            return []
        an_accounts = self.env['sale.subscription'].read_group([('id', operator, value)], ['analytic_account_id'], ['analytic_account_id'])
        aa_ids = [aa['analytic_account_id'][0] for aa in an_accounts]

        return [('project_id', operator, aa_ids)]

    update_contract = fields.Boolean("Update Contract", help="If set, the associated contract will be overwritten by this sale order (every recurring line of the contract not in this sale order will be deleted).")
    subscription_id = fields.Many2one('sale.subscription', 'Subscription', compute=_get_subscription, search=_search_subscription)

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            purchase_lines_to_create = []
            external_order = False
            external_provider = False
            for line in order.order_line:
                if line.product_id.automatic_supply:
                    external_order = True
                    external_provider = line.product_id.external_provider.id
                    purchase_lines_to_create.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'sold_quantity': line.product_uom_qty,
                        'uom_id': line.product_uom.id,
                        'price_unit': line.price_unit,
                        'discount': line.discount if line.order_id.update_contract else False,
                    }))

            if external_order and purchase_lines_to_create:
                purchase_order = {'partner_id': external_provider,
                                  'lines': purchase_lines_to_create}
                #TODO: Create Purchase Order

        return res