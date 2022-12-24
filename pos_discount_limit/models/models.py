# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    discount_pc_limit = fields.Float(string='Discount Limit (%) ', help='Discount percentage limit', default=0.0)

    @api.constrains('discount_pc_limit')
    def _check_negative_value(self):
        for record in self:
            if record.discount_pc_limit < 0:
                raise ValidationError(_("Discount rate should be positive"))
