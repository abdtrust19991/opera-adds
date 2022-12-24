""" Initialize Mrp Overhead Cost """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class MrpOverheadCostLine(models.Model):
    """
        Initialize Mrp Overhead Cost Line:
         -
    """
    _name = 'mrp.overhead.cost.line'
    _description = 'Mrp Overhead Cost Line'

    production_id = fields.Many2one(
        'mrp.production'
    )
    workorder_id = fields.Many2one(
        'mrp.workorder'
    )
    workcenter_id = fields.Many2one(
        'mrp.workcenter',
        related='workorder_id.workcenter_id'
    )
    estimated_moh_ids = fields.Many2many(
        'product.product',
        relation='estimated_moh_rel',
        column1='product_id',
        column2='work_center',
    )
    actual_moh_ids = fields.Many2many(
        'product.product',
        relation='actual_moh_rel',
        column1='product_id_2',
        column2='work_center_2',
        domain="[('can_be_moh', '=', True)]",
    )
    total_cost_per_hour = fields.Float(
        compute='_compute_total_cost_per_hour'
    )
    total_estimated_cost = fields.Float(
        compute='_compute_total_estimated_cost'
    )
    total_actual_cost = fields.Float(
        compute='_compute_total_actual_cost'
    )

    @api.depends('actual_moh_ids')
    def _compute_total_cost_per_hour(self):
        """ Compute total_cost_per_hour value """
        for rec in self:
            if rec.actual_moh_ids:
                rec.total_cost_per_hour = sum(rec.actual_moh_ids.mapped('standard_price'))
            else:
                rec.total_cost_per_hour = 0

    def _compute_total_estimated_cost(self):
        """ Compute total_estimated_cost value """
        for rec in self:
            if rec.workorder_id and rec.total_cost_per_hour:
                rec.total_estimated_cost = rec.workorder_id.duration_expected * (rec.total_cost_per_hour / 60)
            else:
                rec.total_estimated_cost = 0

    def _compute_total_actual_cost(self):
        """ Compute total_actual_cost value """
        for rec in self:
            if rec.workorder_id and rec.total_cost_per_hour:
                rec.total_actual_cost = rec.workorder_id.duration * (rec.total_cost_per_hour / 60)
            else:
                rec.total_actual_cost = 0
