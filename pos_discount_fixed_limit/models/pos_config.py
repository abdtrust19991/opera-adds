# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    discount_fixed = fields.Float(string='Cash Discount', default=5, help='The default fixed cash discount')

    @api.onchange('company_id', 'module_pos_discount')
    def _default_discount_product_id(self):
        res = super(PosConfig, self)._default_discount_product_id()
        if self.module_pos_discount:
            self.discount_fixed = 5
        else:
            self.discount_fixed = 0.0
        return res
