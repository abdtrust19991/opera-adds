""" Initialize Workorder """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class MrpWorkorder(models.Model):
    """
        Inherit Mrp Workorder:
         -
    """
    _inherit = 'mrp.workorder'

    def unlink(self):
        """ Override unlink """
        for rec in self:
            labour = self.env['direct.labour.line'].search([
                ('workorder_id', '=', rec.id)
            ])
            labour.unlink()
            over_head = self.env['mrp.overhead.cost.line'].search([
                ('workorder_id', '=', rec.id)
            ])
            over_head.unlink()
        return super(MrpWorkorder, self).unlink()

    @api.constrains('date_planned_start')
    def _onchange_date_planned_start(self):
        """ date_planned_start """
        for rec in self:
            labour = self.env['direct.labour.line'].search([
                ('workorder_id', '=', rec.id)
            ])
            employee_shift = self.env['employee.shift'].search([
                ('work_center_id', '=', rec.workcenter_id.id),
                ('date_from', '<=', rec.date_planned_start),
                ('date_to', '>=', rec.date_planned_start),
                ('state', '!=', 'done'),
            ], limit=1)
            estimated_employee_ids = employee_shift.employee_shift_line_ids.mapped('employee_id')
            total_cost_per_hour = sum(employee_shift.employee_shift_line_ids.mapped('cost_per_hour'))
            labour.update({
                'workorder_id': rec.id,
                'production_id': rec.production_id.id,
                'employee_shift_id': employee_shift.id,
                'estimated_employee_ids': estimated_employee_ids.ids,
                # 'actual_employee_ids': estimated_employee_ids.ids,
                'total_cost_per_hour': total_cost_per_hour,
            })
