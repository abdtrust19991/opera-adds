# -*- coding: utf-8 -*-
""" init object """
import treepoem
import base64
from io import BytesIO
from odoo import fields, models, api, _

import logging

LOGGER = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_barcode_tree_image(self):
        for rec in self:
            if rec.barcode:
                image = treepoem.generate_barcode(barcode_type='code128', data=rec.barcode)
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                barcode_image = base64.b64encode(buffered.getvalue())
                return barcode_image

    def get_product_print_data(self):
        return{
            'display_name': self.display_name,
            'price': self.lst_price,
            'barcode_image': self.get_barcode_tree_image(),
            'currency_id': self.company_id.currency_id or self.env.company.currency_id ,
            'barcode': self.barcode,
        }




