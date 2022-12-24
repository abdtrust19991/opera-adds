# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _

import logging

LOGGER = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_return_password = fields.Boolean('Allow Return & Orders Pwd')
    return_order_password = fields.Char(u'password')

    return_order_duration = fields.Integer(string="Return/Reprint Order Duration", default=7, required=False, )
    return_order_by_barcode_duration = fields.Integer(string="", default=7, required=False, )