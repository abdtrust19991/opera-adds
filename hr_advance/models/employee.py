# -*- coding: utf-8 -*-

from odoo import api, fields, models, _,exceptions
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta



class employee(models.Model):
    _inherit = 'hr.employee'

    advance_amount = fields.Float(string="Advance Amount",  required=False,compute="_compute_advance_amount"  )
    address_home_id = fields.Many2one(
        'res.partner', 'Private Address', help='Enter here the private address of the employee, not the one linked to your company.',groups=None)

    def _compute_advance_amount(self):
        today = fields.Date.today()
        for rec in self:
            total=0.0
            advances = self.env['pay.advance.line'].search([('employee_id', '=', rec.id),('is_post', '=', False)])
            for line in advances:
                if line.due_date <= today:
                    line.write({'is_post':True})
                    total += line.amount
            rec.advance_amount = total





