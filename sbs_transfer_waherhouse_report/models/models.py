# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    carrier_id = fields.Many2one('delivery.carrier',string="Shippment")
    follow_number = fields.Char(string="رقم التتبع ")
