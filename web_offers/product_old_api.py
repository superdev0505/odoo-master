# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import time

import openerp
from openerp import api, tools, SUPERUSER_ID
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import psycopg2

import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round, float_compare
from openerp.exceptions import UserError
from openerp.exceptions import except_orm


class product_template(osv.osv):
    _inherit = "product.template"

    def _product_template_price(self, cr, uid, ids, name, arg, context=None):
        plobj = self.pool.get('product.pricelist')
        res = {}
        quantity = context.get('quantity') or 1.0
        pricelist = context.get('pricelist', False)
        partner = context.get('partner', False)

        affiliate = context.get('affiliate', False)
        if affiliate:
            affiliate_obj = self.pool.get('crm.team').browse(cr, uid, affiliate)
            if affiliate_obj.pricelist_id:
                pricelist = affiliate_obj.pricelist_id.id

        #promotion_code = context.get('promotion', False)
        #if promotion_code:
        #    pricelist_id = plobj.search(cr, uid, [('code','=', promotion_code)])
        #    if pricelist_id:
        #        pricelist = pricelist_id[0]

        if pricelist:
            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist, basestring):
                pricelist_ids = plobj.name_search(
                    cr, uid, pricelist, operator='=', context=context, limit=1)
                pricelist = pricelist_ids[0][0] if pricelist_ids else pricelist

            if isinstance(pricelist, (int, long)):
                products = self.browse(cr, uid, ids, context=context)
                qtys = map(lambda x: (x, quantity, partner), products)
                pl = plobj.browse(cr, uid, pricelist, context=context)
                price = plobj._price_get_multi(cr, uid, pl, qtys, context=context)
                for id in ids:
                    res[id] = price.get(id, 0.0)
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    def _product_promo_price(self, cr, uid, ids, name, arg, context=None):
        plobj = self.pool.get('product.pricelist')
        res = {}
        quantity = context.get('quantity') or 1.0
        pricelist = context.get('pricelist', False)
        partner = context.get('partner', False)

        affiliate = context.get('affiliate', False)
        if affiliate:
            affiliate_obj = self.pool.get('crm.team').browse(cr, uid, affiliate)
            if affiliate_obj.pricelist_id:
                pricelist = affiliate_obj.pricelist_id.id

        promotion_code = context.get('promotion', False)
        if promotion_code:
            pricelist_id = plobj.search(cr, uid, [('code', '=', promotion_code)])
            if pricelist_id:
                pricelist = pricelist_id[0]

        if pricelist:
            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist, basestring):
                pricelist_ids = plobj.name_search(
                    cr, uid, pricelist, operator='=', context=context, limit=1)
                pricelist = pricelist_ids[0][0] if pricelist_ids else pricelist

            if isinstance(pricelist, (int, long)):
                products = self.browse(cr, uid, ids, context=context)
                qtys = map(lambda x: (x, quantity, partner), products)
                pl = plobj.browse(cr, uid, pricelist, context=context)
                price = plobj._price_get_multi(cr, uid, pl, qtys, context=context)
                for id in ids:
                    res[id] = price.get(id, 0.0)
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    def _set_product_template_price(self, cr, uid, id, name, value, args, context=None):
        product_uom_obj = self.pool.get('product.uom')

        product = self.browse(cr, uid, id, context=context)
        if 'uom' in context:
            uom = product.uom_id
            value = product_uom_obj._compute_price(cr, uid,
                                                   context['uom'], value, uom.id)

        return product.write({'list_price': value})

    _columns = {
        'price': fields.function(_product_template_price, fnct_inv=_set_product_template_price, type='float',
                                 string='Price', digits_compute=dp.get_precision('Product Price')),
        'promotion_price': fields.function(_product_promo_price, type='float',
                                 string='Promotion Price', digits_compute=dp.get_precision('Product Price')),
    }


class product_product(osv.osv):
    _inherit = "product.product"

    def _product_price(self, cr, uid, ids, name, arg, context=None):
        plobj = self.pool.get('product.pricelist')
        res = {}
        if context is None:
            context = {}
        quantity = context.get('quantity') or 1.0
        pricelist = context.get('pricelist', False)
        partner = context.get('partner', False)

        affiliate = context.get('affiliate', False)
        if affiliate:
            affiliate_obj = self.pool.get('crm.team').browse(cr, uid, affiliate)
            if affiliate_obj.pricelist_id:
                pricelist = affiliate_obj.pricelist_id.id

        if pricelist:
            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist, basestring):
                pricelist_ids = plobj.name_search(
                    cr, uid, pricelist, operator='=', context=context, limit=1)
                pricelist = pricelist_ids[0][0] if pricelist_ids else pricelist

            if isinstance(pricelist, (int, long)):
                products = self.browse(cr, uid, ids, context=context)
                qtys = map(lambda x: (x, quantity, partner), products)
                pl = plobj.browse(cr, uid, pricelist, context=context)
                price = plobj._price_get_multi(cr, uid, pl, qtys, context=context)
                for id in ids:
                    res[id] = price.get(id, 0.0)
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    def _set_product_lst_price(self, cr, uid, id, name, value, args, context=None):
        product_uom_obj = self.pool.get('product.uom')

        product = self.browse(cr, uid, id, context=context)
        if 'uom' in context:
            uom = product.uom_id
            value = product_uom_obj._compute_price(cr, uid,
                                                   context['uom'], value, uom.id)
        value = value - product.price_extra

        return product.write({'list_price': value})

    _columns = {
        'price': fields.function(_product_price, fnct_inv=_set_product_lst_price, type='float', string='Price',
                                 digits_compute=dp.get_precision('Product Price')),
    }