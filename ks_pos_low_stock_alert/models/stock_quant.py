# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def get_available_quantity(self, product_ids, location_id, lot_id=None, package_id=None, owner_id=None,
                               strict=False,
                               allow_negative=False):
        product_ids = self.env['product.product'].browse(product_ids)
        location_id = self.env['stock.location'].browse(location_id)

        qty_products = []
        qty = 0
        for product_id in product_ids:
            qty = self._get_available_quantity(product_id, location_id, lot_id, package_id, owner_id, strict,
                                               allow_negative)
            qty_products.append({'id': product_id.id, 'qty': qty})
        return qty_products
