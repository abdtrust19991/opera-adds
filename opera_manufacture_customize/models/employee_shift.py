""" Initialize Employee Shift """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class EmployeeShift(models.Model):
    """
        Initialize Employee Shift:
         - 
    """
    _name = 'employee.shift'
    _description = 'Employee Shift'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    work_center_id = fields.Many2one(
        'mrp.workcenter',
        copy=False
    )
    date_from = fields.Datetime(
        required=1
    )
    date_to = fields.Datetime(
        required=1
    )
    employee_shift_line_ids = fields.One2many(
        'employee.shift.line',
        'employee_shift_id'
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'), 
         ('run', 'Running'), 
         ('done', 'Done')],
        default='draft',
        string='Status',
    )
    current_day = fields.Datetime(
        compute='_compute_current_day'
    )
    workorder_ids = fields.Many2many(
        'mrp.workorder',
        compute='_compute_workorder_ids'
    )
    shift_assigned = fields.Boolean(
        compute='_compute_shift_assigned'
    )

    def unlink(self):
        """ Override unlink """
        if self.state != 'draft':
            raise ValidationError('You can delete only draft shift !')
        return super(EmployeeShift, self).unlink()

    @api.depends('employee_shift_line_ids')
    def _compute_shift_assigned(self):
        """ Compute shift_assigned value """
        for rec in self:
            if rec.employee_shift_line_ids:
                rec.shift_assigned = True
            else:
                rec.shift_assigned = False

    def name_get(self):
        result = []
        for record in self:
            if record.work_center_id:
                name = ' ['+record.work_center_id.name + ']' + ' From: ' + str(record.date_from) +' To: '+ str(record.date_to)
                result.append((record.id,name))
        return result

    @api.constrains('work_center_id')
    def _check_work_center_id(self):
        """ Validate  """
        for rec in self:
            if rec.work_center_id and rec.date_to and rec.date_from:
                shifts = self.env['employee.shift'].search([
                    ('work_center_id', '=', rec.work_center_id.id),
                    ('date_from', '<=', rec.date_from),
                    ('date_to', '>=', rec.date_from),
                    ('state', '!=', 'done'),
                ])
                if len(shifts) > 1:
                    raise ValidationError('You can not make more than shift for same work center in same range !')

    def write(self, vals):
        """ Override write """
        mo_state = self.env['mrp.workorder'].search([
            ('workcenter_id', '=', self.work_center_id.id),
            ('state', '!=', 'done'),
            ('date_planned_start', '>=', self.date_from),
            ('date_planned_start', '<=', self.date_to),
        ]).mapped('production_id').mapped('state')
        if 'planned' in mo_state:
            raise ValidationError('You can not edit when manufacture order in planned state !')
        res = super(EmployeeShift, self).write(vals)
        return res

    def _compute_workorder_ids(self):
        """ Compute production_ids value """
        for rec in self:
            workorder = self.env['mrp.workorder'].search([
                ('workcenter_id', '=', rec.work_center_id.id),
                ('state', '=', 'progress'),
                ('date_planned_start', '>=', rec.date_from),
                ('date_planned_start', '<=', rec.date_to),
            ])
            if workorder:
                rec.workorder_ids = workorder
            else:
                rec.workorder_ids = None

    def _compute_current_day(self):
        """ Compute current_day value """
        for rec in self:
            rec.current_day = fields.Datetime.now()
            rec._check_state()

    def _check_state(self):
        """ Compute state value """
        for rec in self:
            if rec.state == 'confirm' and rec.date_from <= rec.current_day:
                rec.write({
                    'state': 'run'
                })
            if rec.state == 'run' and rec.date_to <= rec.current_day and not rec.workorder_ids:
                rec.write({
                    'state': 'done',
                    'date_to': fields.Datetime.now(),
                })

    def action_confirm(self):
        """ Action Confirm """
        for rec in self:
            rec.write({
                'state': 'confirm'
            })
            rec._check_state()

    def action_set_to_draft(self):
        """ Action Confirm """
        for rec in self:
            rec.write({
                'state': 'draft'
            })

    def action_done(self):
        """ Action Confirm """
        for rec in self:
            mo_state = self.env['mrp.workorder'].search([
                ('workcenter_id', '=', rec.work_center_id.id),
                ('state', '!=', 'done'),
                ('date_planned_start', '>=', rec.date_from),
                ('date_planned_start', '<=', rec.date_to),
            ]).mapped('production_id').mapped('state')
            if 'planned' in mo_state:
                raise ValidationError('You can not edit when manufacture order in planned state !')
            if not rec.workorder_ids:
                rec.write({
                    'state': 'done',
                    'date_to': fields.Datetime.now(),
                })
            else:
                raise ValidationError('There is some orders must finished first !')


class EmployeeShiftLine(models.Model):
    """
        Initialize Employee Shift Line:
         - 
    """
    _name = 'employee.shift.line'
    _description = 'Employee Shift Line'

    _sql_constraints = [
        ('unique_employee_shift',
         'UNIQUE(employee_shift_id,employee_id)',
         'Employee must be unique'),
    ]

    employee_shift_id = fields.Many2one(
        'employee.shift',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        domain="[('is_technical', '=', True)]"
    )
    cost_per_hour = fields.Float(
        related='employee_id.cost_per_hour'
    )
