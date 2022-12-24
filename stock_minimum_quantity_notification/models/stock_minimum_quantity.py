# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging
LOGGER = logging.getLogger(__name__)


class StockMinQty(models.Model):
    _name = 'stock.minimum.quantity'
    _description = 'Stock Minimum Quantity Notification'
    _inherit = 'mail.thread'

    name = fields.Char(compute="_compute_record_name")

    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
    )
    min_qty = fields.Float(string="Minimum Quantity", required=True, )
    warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse",
        string="Warehouses",
        ondelete='restrict'
    )
    location_ids = fields.Many2many(
        'stock.location',
        string="Locations",
        ondelete='restrict'
    )

    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Users To Notify",
    )
    active = fields.Boolean(default=True)

    @api.constrains('min_qty')
    def _check_min_qty(self):
        if not self.min_qty:
            raise ValidationError(_("Min Qty can't be zero"))

    @api.depends('product_id')
    def _compute_record_name(self):
        for record in self:
            if record.product_id:
                record.name = record.product_id.display_name + " Stock Alert"

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.update({'name': self.product_id.display_name + " Stock Alert"})

    @api.onchange('warehouse_ids')
    def _onchange_warehouse_ids(self):
        if self.warehouse_ids:
            domain = [('location_id', 'child_of', self.warehouse_ids.mapped('view_location_id').ids)]
            return {'domain': {'location_ids': domain}}

    def check_min_qty(self):
        records = self.search([])
        for record in records:
            warehouses = record.warehouse_ids or self.env['stock.warehouse'].search([])
            locations = record.location_ids or self.env['stock.location'].search(
                [('location_id', 'child_of', warehouses.mapped('view_location_id').ids)])
            product = record.product_id
            qty = product.with_context(location=locations.ids).qty_available
            if record.min_qty and qty <= record.min_qty:
                partners = record.user_ids.mapped('partner_id')
                partners = partners and partners.ids
                message = "product %s reached the minimum qty %s" % (product.name, str(record.min_qty))
                record.message_post(subject="Stock Alert", body=message, subtype='mt_comment', partner_ids=partners)
