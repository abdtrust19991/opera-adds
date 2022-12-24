# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    stock_request_ids = fields.One2many(
        comodel_name="stock.request",
        string="Stock Requests",
        compute="_compute_stock_request_ids",
    )
    stock_request_count = fields.Integer(
        "Stock Request #", compute="_compute_stock_request_ids"
    )

    @api.depends("move_lines")
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_ids = rec.move_lines.mapped("stock_request_ids")
            rec.stock_request_count = len(rec.stock_request_ids)

    def action_view_stock_request(self):
        """
        :return dict: dictionary value for created view
        """
        action = self.env.ref("opera_stock_request.action_stock_request_form").read()[0]

        requests = self.mapped("stock_request_ids")
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("opera_stock_request.view_stock_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        return action

    def write(self, vals):
        """ Override write """
        res = super(StockPicking, self).write(vals)
        self._onchange_origin()
        return res

    @api.model
    def create(self, vals_list):
        """ Override create """
        # vals_list ={'field': value}  -> dectionary contains only new filled fields
        self._onchange_origin()
        return super(StockPicking, self).create(vals_list)

    @api.constrains('origin')
    @api.onchange('origin')
    def _onchange_origin(self):
        """ origin """
        for rec in self:
            stock_request_order = self.env['stock.request.order'].search([('name', '=', rec.origin)])
            if stock_request_order and not rec.stock_request_ids and rec.picking_type_id.code == 'outgoing':
                stock_request_order.update({
                    'delivery_picking_id': rec.id
                })
