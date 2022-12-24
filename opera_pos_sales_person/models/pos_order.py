# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    sale_person_code = fields.Char()
    sale_person_id = fields.Many2one(comodel_name="hr.employee")
    user_id = fields.Many2one(comodel_name="res.users", string="Cashier")

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)

        if ui_order.get('sale_person_code', False):
            order_fields.update({
                'sale_person_code': ui_order['sale_person_code']
            })

        if ui_order.get('sale_person_id', False):
            order_fields.update({
                'sale_person_id': ui_order['sale_person_id']
            })

        return order_fields

    def print_pos_receipt(self):
        data = super(PosOrder,self).print_pos_receipt()
        data.append(self.sale_person_id.name)
        return data

