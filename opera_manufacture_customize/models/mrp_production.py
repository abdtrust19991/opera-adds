""" Initialize Mrp Production """

import json
import datetime
import math
import operator as py_operator
import re

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import format_date

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES

SIZE_BACK_ORDER_NUMERING = 3


class MrpProduction(models.Model):
    """
        Inherit Mrp Production:
         -
    """
    _inherit = 'mrp.production'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')])

    direct_labour_line_ids = fields.One2many(
        'direct.labour.line',
        'production_id'
    )
    overhead_cost_line_ids = fields.One2many(
        'mrp.overhead.cost.line',
        'production_id'
    )
    direct_material_ids = fields.One2many(
        'direct.material',
        'production_id'
    )
    direct_material_checked = fields.Boolean(
        copy=0
    )

    total_estimated_direct_material = fields.Float(
        compute='_compute_total_estimated_direct_material'
    )
    total_actual_direct_material = fields.Float(
        compute='_compute_total_actual_direct_material'
    )
    variance_direct_material = fields.Float(
        compute='_compute_variance_direct_material'
    )

    total_estimated_labour = fields.Float(
        compute='_compute_total_estimated_labour'
    )
    total_actual_labour = fields.Float(
        compute='_compute_total_actual_labour'
    )
    variance_labour = fields.Float(
        compute='_compute_variance_labour'
    )

    total_estimated_moh = fields.Float(
        compute='_compute_total_estimated_moh'
    )
    total_actual_moh = fields.Float(
        compute='_compute_total_actual_moh'
    )
    variance_moh = fields.Float(
        compute='_compute_variance_moh'
    )
    total_estimated_cost = fields.Float(
        compute='_compute_total_estimated_cost'
    )
    total_actual_cost = fields.Float(
        compute='_compute_total_actual_cost'
    )
    total_variance = fields.Float(
        compute='_compute_total_variance'
    )
    sale_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        compute='_compute_sale_id'
    )
    direct_material_done = fields.Boolean(
        copy=False
    )
    backorder_validated = fields.Boolean(
        copy=False
    )
    
    # @api.constrains('backorder_sequence')
    # @api.onchange('backorder_sequence')
    # def _check_backorder_sequence(self):
    #     """ Validate backorder_sequence """
    #     for rec in self:
    #         if rec.backorder_sequence and rec.backorder_sequence > 1:
    #             rec.action_cancel()

    # @api.model
    # def create(self, vals_list):
    #     """ Override create """
    #     # vals_list ={'field': value}  -> dectionary contains only new filled fields
    #     res = super(MrpProduction, self).create(vals_list)
    #     for rec in res:
    #         if rec.backorder_sequence and rec.backorder_sequence > 1:
    #             rec.action_cancel()
    #     return res

    @api.depends('origin')
    def _compute_sale_id(self):
        """ Compute sale_id value """
        for rec in self:
            if rec.origin and rec.origin.startswith('S0'):
                sale = self.env['sale.order'].search([('name', '=', rec.origin)])
                if sale:
                    rec.sale_id = sale.id
                else:
                    rec.sale_id = None
            else:
                rec.sale_id = None

    @api.depends('total_estimated_moh', 'total_estimated_labour', 'total_estimated_direct_material')
    def _compute_total_estimated_cost(self):
        """ Compute total_estimated_cost value """
        for rec in self:
            rec.total_estimated_cost = rec.total_estimated_direct_material + rec.total_estimated_moh + rec.total_estimated_labour

    @api.depends('total_actual_moh', 'total_actual_labour', 'total_actual_direct_material')
    def _compute_total_actual_cost(self):
        """ Compute total_actual_cost value """
        for rec in self:
            rec.total_actual_cost = rec.total_actual_direct_material + rec.total_actual_labour + rec.total_actual_moh

    @api.depends('variance_moh', 'variance_labour', 'variance_direct_material')
    def _compute_total_variance(self):
        """ Compute total_variance value """
        for rec in self:
            rec.total_variance = rec.variance_labour + rec.variance_moh + rec.variance_direct_material

    @api.depends('direct_material_ids')
    def _compute_total_estimated_direct_material(self):
        """ Compute  value """
        for rec in self:
            if rec.direct_material_ids:
                rec.total_estimated_direct_material = sum(rec.direct_material_ids.mapped('total_planned_cost'))
            else:
                rec.total_estimated_direct_material = 0

    @api.depends('direct_material_ids')
    def _compute_total_actual_direct_material(self):
        """ Compute  value """
        for rec in self:
            if rec.direct_material_ids:
                rec.total_actual_direct_material = sum(rec.direct_material_ids.mapped('total_actual_cost'))
            else:
                rec.total_actual_direct_material = 0

    @api.depends('direct_labour_line_ids')
    def _compute_total_estimated_labour(self):
        """ Compute  value """
        for rec in self:
            if rec.direct_labour_line_ids:
                rec.total_estimated_labour = sum(rec.direct_labour_line_ids.mapped('total_estimated_cost'))
            else:
                rec.total_estimated_labour = 0

    @api.depends('direct_labour_line_ids')
    def _compute_total_actual_labour(self):
        """ Compute  value """
        for rec in self:
            if rec.direct_labour_line_ids:
                rec.total_actual_labour = sum(rec.direct_labour_line_ids.mapped('total_actual_cost'))
            else:
                rec.total_actual_labour = 0

    @api.depends('total_estimated_labour', 'total_actual_labour')
    def _compute_variance_labour(self):
        """ Compute  value """
        for rec in self:
            rec.variance_labour = rec.total_estimated_labour - rec.total_actual_labour

    @api.depends('overhead_cost_line_ids')
    def _compute_total_estimated_moh(self):
        """ Compute  value """
        for rec in self:
            if rec.overhead_cost_line_ids:
                rec.total_estimated_moh = sum(rec.overhead_cost_line_ids.mapped('total_estimated_cost'))
            else:
                rec.total_estimated_moh = 0

    @api.depends('overhead_cost_line_ids')
    def _compute_total_actual_moh(self):
        """ Compute  value """
        for rec in self:
            if rec.overhead_cost_line_ids:
                rec.total_actual_moh = sum(rec.overhead_cost_line_ids.mapped('total_actual_cost'))
            else:
                rec.total_actual_moh = 0

    @api.depends('total_estimated_moh', 'total_actual_moh')
    def _compute_variance_moh(self):
        """ Compute  value """
        for rec in self:
            rec.variance_moh = rec.total_estimated_moh - rec.total_actual_moh

    @api.depends('total_estimated_direct_material', 'total_actual_direct_material')
    def _compute_variance_direct_material(self):
        """ Compute  value """
        for rec in self:
            rec.variance_direct_material = rec.total_estimated_direct_material - rec.total_actual_direct_material

    def check_plan_update(self):
        """ Check Plan Update """

        employee_shifts = self.env['employee.shift'].search([
            ('state', '=', 'run'),
        ])
        for shift in employee_shifts:
            shift._check_state()
        for line in self.workorder_ids:
            employee_shift = self.env['employee.shift'].search([
                ('work_center_id', '=', line.workcenter_id.id),
                ('date_from', '<=', line.date_planned_start),
                ('date_to', '>=', line.date_planned_start),
                ('state', '!=', 'done'),
            ], limit=1)
            estimated_employee_ids = employee_shift.employee_shift_line_ids.mapped('employee_id')
            self.env['direct.labour.line'].create({
                'workorder_id': line.id,
                'production_id': self.id,
                'employee_shift_id': employee_shift.id,
                'estimated_employee_ids': estimated_employee_ids.ids,
                'actual_employee_ids': estimated_employee_ids.ids,
            })
            if line.workcenter_id.workcenter_overhead_cost_line_ids:
                self.env['mrp.overhead.cost.line'].create({
                    'workorder_id': line.id,
                    'production_id': self.id,
                    'estimated_moh_ids': line.workcenter_id.workcenter_overhead_cost_line_ids.mapped('product_id').ids,
                    'actual_moh_ids': line.workcenter_id.workcenter_overhead_cost_line_ids.mapped('product_id').ids,
                })

    def button_mark_done(self):
        """ Override button_mark_done """
        # res =
        if self.qty_producing <= 0:
            raise ValidationError('You must set producing quantity !')
        employee_shifts = self.env['employee.shift'].search([
            ('state', '=', 'run'),
        ])
        for shift in employee_shifts:
            shift._check_state()
        if not self.direct_material_done:
            for line in self.move_raw_ids:
                material = self.env['direct.material'].search([
                    ('product_id', '=', line.product_id.id),
                    ('production_id', '=', self.id),
                ],limit=1)
                if material:
                    # for mat in material:
                    material.update({
                        'actual_qty': material.actual_qty + line.quantity_done,
                        # 'planned_qty': line.planned_qty ,
                    })
                else:
                    if self.backorder_sequence > 1:
                        self.env['direct.material'].create({
                            'production_id': self.id,
                            'product_id': line.product_id.id,
                            'uom_id': line.product_uom.id,
                            'planned_qty': line.should_consume_qty,
                            'actual_qty': line.quantity_done,
                            # 'cost_per_uit': line.product_id.standard_price,
                        })
                    else:
                        self.env['direct.material'].create({
                            'production_id': self.id,
                            'product_id': line.product_id.id,
                            'uom_id': line.product_uom.id,
                            'planned_qty': 0,
                            'actual_qty': line.quantity_done,
                            # 'cost_per_uit': line.product_id.standard_price,
                        })
                self.direct_material_done = True

        for work in self.workorder_ids:
            total = 0
            direct = self.direct_labour_line_ids.filtered(lambda x: x.workcenter_id == work.workcenter_id)
            over_head = self.overhead_cost_line_ids.filtered(lambda x: x.workcenter_id == work.workcenter_id)
            if over_head:
                total += sum(over_head.mapped('total_cost_per_hour'))
            if direct:
                total += sum(direct.mapped('total_cost_per_hour'))
            work.workcenter_id.update({
                'costs_hour': total
            })
        return super(MrpProduction, self).button_mark_done()

    def button_plan(self):
        """ Create work orders. And probably do stuff, like things. """
        orders_to_plan = self.filtered(lambda order: not order.is_planned)
        orders_to_confirm = orders_to_plan.filtered(lambda mo: mo.state == 'draft')
        if self.state != 'draft':
            orders_to_confirm.action_confirm()
        for order in orders_to_plan:
            order._plan_workorders()
        self.check_plan_update()
        self.write({
            'state': 'planned'
        })
        return True

    @api.onchange('qty_producing')
    def _onchange_qty_producing(self):
        """ qty_producing """
        for line in self.move_raw_ids:
            product = self.move_raw_ids.filtered(lambda x: x.product_id == line.product_id)
            material = self.env['direct.material'].search([
                ('product_id', '=', line.product_id.id),
                ('production_id', '=', self.ids),
            ], limit=1)
            if material:
                if len(product) > 1:
                    if line == product[0]:
                        material.update({
                            'planned_qty': line.should_consume_qty,
                        })
                else:
                    material.update({
                        'planned_qty': line.should_consume_qty,
                    })

    def action_confirm(self):
        """ Override action_confirm """
        res = super(MrpProduction, self).action_confirm()

        if self.direct_labour_line_ids:
            for line in self.direct_labour_line_ids:
            # if line.employee_shift_id.state != 'run':
            #     raise ValidationError('You can not confirm with shift not in running state !')
                if not line.estimated_employee_ids:
                    raise ValidationError('You can not confirm with shift has not in estimated employees !')
        if not self.direct_material_checked:
            for line in self.move_raw_ids:
                self.env['direct.material'].create({
                        'production_id': self.id,
                        'product_id': line.product_id.id,
                        'uom_id': line.product_uom.id,
                        # 'planned_qty': line.product_uom_qty,
                        # 'actual_qty': line.quantity_done,
                        # 'cost_per_uit': line.product_id.standard_price,
                    })
        self.direct_material_checked = True
        self.state = 'confirmed'
        if not self.backorder_validated and self.backorder_sequence > 1:
            self.action_draft()
            self.qty_producing = 0
            self.direct_material_ids.unlink()
            self.backorder_validated = True
        return res

    def update_workorder_quantity(self):
        """ Update Workorder Quantity """
        for rec in self:
            for work in rec.workorder_ids:
                work.sudo().write({
                    'qty_done': rec.qty_producing,
                    'qty_produced': rec.qty_producing,
                })

    def button_unplan(self):
        """ Override button_unplan """
        self.direct_labour_line_ids.sudo().unlink()
        self.overhead_cost_line_ids.sudo().unlink()
        self.write({
            'state': 'draft'
        })
        return super(MrpProduction, self).button_unplan()

    # def _generate_backorder_productions(self, close_mo=True):
    #     backorders = self.env['mrp.production']
    #     for production in self:
    #         if production.backorder_sequence == 0:  # Activate backorder naming
    #             production.backorder_sequence = 1
    #         production.name = self._get_name_backorder(production.name, production.backorder_sequence)
    #         backorder_mo = production.copy(default=production._get_backorder_mo_vals())
    #         if close_mo:
    #             production.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')).write({
    #                 'raw_material_production_id': backorder_mo.id,
    #             })
    #             production.move_finished_ids.filtered(lambda m: m.state not in ('done', 'cancel')).write({
    #                 'production_id': backorder_mo.id,
    #             })
    #         else:
    #             new_moves_vals = []
    #             for move in production.move_raw_ids | production.move_finished_ids:
    #                 if not move.additional:
    #                     qty_to_split = move.product_uom_qty - move.unit_factor * production.qty_producing
    #                     qty_to_split = move.product_uom._compute_quantity(qty_to_split, move.product_id.uom_id, rounding_method='HALF-UP')
    #                     move_vals = move._split(qty_to_split)
    #                     if not move_vals:
    #                         continue
    #                     if move.raw_material_production_id:
    #                         move_vals[0]['raw_material_production_id'] = backorder_mo.id
    #                     else:
    #                         move_vals[0]['production_id'] = backorder_mo.id
    #                     new_moves_vals.append(move_vals[0])
    #             new_moves = self.env['stock.move'].create(new_moves_vals)
    #         backorders |= backorder_mo
    #         first_wo = self.env['mrp.workorder']
    #         for old_wo, wo in zip(production.workorder_ids, backorder_mo.workorder_ids):
    #             wo.qty_produced = max(old_wo.qty_produced - old_wo.qty_producing, 0)
    #             if wo.product_tracking == 'serial':
    #                 wo.qty_producing = 1
    #             else:
    #                 wo.qty_producing = wo.qty_remaining
    #             if wo.qty_producing == 0:
    #                 wo.action_cancel()
    #             if not first_wo and wo.state != 'cancel':
    #                 first_wo = wo
    #         first_wo.state = 'ready'
    #
    #         # We need to adapt `duration_expected` on both the original workorders and their
    #         # backordered workorders. To do that, we use the original `duration_expected` and the
    #         # ratio of the quantity really produced and the quantity to produce.
    #         ratio = production.qty_producing / production.product_qty
    #         for workorder in production.workorder_ids:
    #             workorder.duration_expected = workorder.duration_expected * ratio
    #         for workorder in backorder_mo.workorder_ids:
    #             workorder.duration_expected = workorder.duration_expected * (1 - ratio)
    #
    #     # As we have split the moves before validating them, we need to 'remove' the excess reservation
    #     if not close_mo:
    #         # self.move_raw_ids.filtered(lambda m: not m.additional)._do_unreserve()
    #         # self.move_raw_ids.filtered(lambda m: not m.additional)._action_assign()
    #         pass
    #     # Confirm only productions with remaining components
    #     # backorders.filtered(lambda mo: mo.move_raw_ids).action_confirm()
    #     # backorders.filtered(lambda mo: mo.move_raw_ids).action_assign()
    #
    #     # Remove the serial move line without reserved quantity. Post inventory will assigned all the non done moves
    #     # So those move lines are duplicated.
    #     # backorders.move_raw_ids.move_line_ids.filtered(lambda ml: ml.product_id.tracking == 'serial' and ml.product_qty == 0).unlink()
    #     # backorders.move_raw_ids._recompute_state()
    #
    #     return backorders
    #
    # def _post_inventory(self, cancel_backorder=False):
    #     for order in self:
    #         moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
    #         moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
    #         for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
    #             move.product_uom_qty = move.quantity_done
    #         # MRP do not merge move, catch the result of _action_done in order
    #         # to get extra moves.
    #         moves_to_do = moves_to_do._action_done()
    #         moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
    #
    #         finish_moves = order.move_finished_ids.filtered(lambda m: m.product_id == order.product_id and m.state not in ('done', 'cancel'))
    #         # the finish move can already be completed by the workorder.
    #         if not finish_moves.quantity_done:
    #             finish_moves.quantity_done = float_round(order.qty_producing - order.qty_produced, precision_rounding=order.product_uom_id.rounding, rounding_method='HALF-UP')
    #             finish_moves.move_line_ids.lot_id = order.lot_producing_id
    #         order._cal_price(moves_to_do)
    #
    #         moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
    #         moves_to_finish = moves_to_finish._action_done(cancel_backorder=cancel_backorder)
    #         # order.action_assign()
    #         consume_move_lines = moves_to_do.mapped('move_line_ids')
    #         order.move_finished_ids.move_line_ids.consume_line_ids = [(6, 0, consume_move_lines.ids)]
    #     return True
