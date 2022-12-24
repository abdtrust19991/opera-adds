""" Initialize Direct Labour Line """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class DirectLabourLine(models.Model):
    """
        Initialize Direct Labour Line:
         -
    """
    _name = 'direct.labour.line'
    _description = 'Direct Labour Line'

    workorder_id = fields.Many2one(
        'mrp.workorder'
    )
    workcenter_id = fields.Many2one(
        'mrp.workcenter',
        related='workorder_id.workcenter_id'
    )
    schedule_date = fields.Datetime(
        related='workorder_id.date_planned_start'
    )
    employee_shift_id = fields.Many2one(
        'employee.shift'
    )
    estimated_employee_ids = fields.Many2many(
        'hr.employee',
        relation='hr_employee_labour',
        column1='employee_id',
        column2='labour_id'
    )

    actual_employee_ids = fields.Many2many(
        'hr.employee',
        relation='hr_employee_labour_2',
        column1='employee_id_2',
        column2='labour_id_2',
        domain="[('is_technical', '=', True)]"
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
    production_id = fields.Many2one(
        'mrp.production'
    )

    @api.depends('actual_employee_ids')
    def _compute_total_cost_per_hour(self):
        """ Compute total_cost_per_hour value """
        for rec in self:
            if rec.actual_employee_ids:
                rec.total_cost_per_hour = sum(rec.actual_employee_ids.mapped('cost_per_hour'))
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
