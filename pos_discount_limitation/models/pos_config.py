# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosConfig(models.Model):

    _inherit = "pos.config"

    def get_discount_product(self):
        return self.env.ref('pos_discount_limitation.product_product_discount').id

    module_pos_discount = fields.Boolean(default=True)
    discount_product_id = fields.Many2one(
        'product.product', default=get_discount_product)

    @api.onchange('module_pos_discount')
    def _onchange_module_pos_discount(self):
        res = super(PosConfig, self)._onchange_module_pos_discount()
        if self.module_pos_discount:
            self.discount_product_id = self.env.ref(
                'pos_discount_limitation.product_product_discount').id
        else:
            self.discount_product_id = False
        self.discount_pc = 0.0
        return res

    @api.model
    def check_user_group(self, pos_user, pc):
        user = pos_user.get('id')
        pos_user_rec = self.env['res.users'].browse(int(user))
        disc_limit = False
        if pos_user_rec.has_group('point_of_sale.group_pos_manager'):
            pos_discount_limitation_rec = self.env['pos.discount.limitation'].search(
                [('group_id', '=', self.env.ref('point_of_sale.group_pos_manager').id)])
            disc_limit = pos_discount_limitation_rec.pos_discount_limitation
        elif pos_user_rec.has_group('point_of_sale.group_pos_user'):
            pos_discount_limitation_rec = self.env['pos.discount.limitation'].search(
                [('group_id', '=', self.env.ref('point_of_sale.group_pos_user').id)])
            disc_limit = pos_discount_limitation_rec.pos_discount_limitation

        if pc > disc_limit:
            return {'disc_limit': disc_limit}
        return True
