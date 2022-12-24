# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _ ,tools, SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from odoo.osv.expression import AND
from datetime import datetime , date ,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from odoo.fields import Datetime as fieldsDatetime
import calendar
from odoo import http
from odoo.http import request
from odoo import tools

import logging

LOGGER = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    barcode = fields.Char(string='Barcode')
    return_order_id = fields.Many2one(comodel_name="pos.order", string="", required=False, )

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)

        if ui_order.get('barcode', False):
            order_fields.update({
                'barcode': ui_order['barcode'],
                'return_order_id': ui_order.get('return_order_id',False),
            })

        return order_fields

    def _export_for_ui(self, order):
        res = super(PosOrder, self)._export_for_ui(order)
        res['sale_person_id'] = order.sale_person_id.id
        res['sale_person_name'] = order.sale_person_id.name
        res['sale_person_code'] = order.sale_person_code
        res['return_order_id'] = order.return_order_id.id
        res['barcode'] = order.barcode
        return res

    @api.model
    def search_paid_order_ids(self, config_id, domain, limit, offset):
        """Search for 'paid' orders that satisfy the given domain, limit and offset."""
        config = self.env['pos.config'].browse(config_id)
        pos_branch = config.pos_branch_id
        now = datetime.now()
        if domain and len(domain) == 1:
            start_date = now + relativedelta(days=-config.return_order_by_barcode_duration)
            default_domain = ['&', ('date_order', '>=', start_date),
                                 '!', '|', ('state', '=', 'draft'),
                              ('state', '=', 'cancelled')]
        else:
            start_date = now + relativedelta(days=-config.return_order_duration)
            default_domain = ['&','&','&',('date_order', '>=', start_date),('config_id.pos_branch_id', '=', pos_branch.id), ('config_id.pos_branch_id', '=', pos_branch.id), '!', '|', ('state', '=', 'draft'), ('state', '=', 'cancelled')]
        real_domain = AND([domain, default_domain])
        ids = self.search(AND([domain, default_domain]), limit=limit, offset=offset).ids
        totalCount = self.search_count(real_domain)
        return {'ids': ids, 'totalCount': totalCount}


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    order_line_id = fields.Many2one(comodel_name="pos.order.line")
    return_line_ids = fields.One2many(comodel_name="pos.order.line", inverse_name="order_line_id")
    return_qty = fields.Float(compute='compute_return_qty')

    @api.depends('return_line_ids', 'return_line_ids.qty')
    def compute_return_qty(self):
        for rec in self:
            quantities = rec.return_line_ids.mapped('qty')
            rec.return_qty = sum(abs(q) for q in quantities)

    def _export_for_ui(self, orderline):
        res = super(PosOrderLine, self)._export_for_ui(orderline)
        res['return_qty'] = orderline.return_qty
        res['order_line_id'] = orderline.order_line_id.id
        return res




