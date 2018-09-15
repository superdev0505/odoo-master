# -*- coding: utf-8 -*-

from openerp import models, fields, api

class sync_offers_wizard(models.TransientModel):
    _name = "sync.offers.wizard"
    _description = "Update Module"

    @api.one
    def sync_data(self):
        self.env['web.api.affiliate.service'].sync_affiliates()
        self.env['web.api.offer.service'].sync_offers()
        return False

