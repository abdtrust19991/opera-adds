# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    lock_price = fields.Boolean(string="Lock price", default=False)
    price_password = fields.Char(string=u"Password")
    lock_discount = fields.Boolean(string="Lock Line discount", default=False)
    discount_password = fields.Char(string=u"Password")
    lock_delete = fields.Boolean(string="Lock delete", default=False)
    delete_password = fields.Char(string=u"Password")
    
    lock_fiscal_position = fields.Boolean(default=False)
    fiscal_position_password = fields.Char(string=u"Password")
    lock_global_discount = fields.Boolean(default=False)
    global_discount_password = fields.Char(string=u"Password")
    lock_delete_order = fields.Boolean(default=False)
    delete_order_pwd = fields.Char(string=u"Password")

    lock_change_sign = fields.Boolean(default=False)
    change_sign_pwd = fields.Char(string=u"Password")

    lock_view_orders = fields.Boolean(string="Lock View Orders",default=False)
    view_orders_pwd = fields.Char(string=u"Password")

    lock_pricselist = fields.Boolean(default=False)
    pricelist_pwd = fields.Char(string=u"Password")

    lock_change_cashier = fields.Boolean(default=False)
    change_cashier_pwd = fields.Char(string=u"Password")


