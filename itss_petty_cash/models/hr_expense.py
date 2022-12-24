# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2018-TODAY .
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrExpenseSheet(models.Model):

    _inherit= "hr.expense.sheet"

    paid_amount = fields.Float(string="Paid amount",  required=False,readonly=True )
    rem_amount = fields.Float(string="Remainder amount",compute="_compute_rem_amount",  required=False, )

    @api.depends('paid_amount')
    def _compute_rem_amount(self):
        self.ensure_one()
        self.rem_amount =self.total_amount - self.paid_amount
        pass

    def petty_pay(self):
        for exp in self:
            view = self.env.ref('itss_petty_cash.petty_pay_wizard_from_view')
            amount = exp.total_amount
            partner_id = self.employee_id.address_home_id.commercial_partner_id.id
            petty_cash_ids=self.env['petty.cash'].search([('employee_id','=',exp.employee_id.id),('state','=','paid')])
            print('petty cash ids is',petty_cash_ids)
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    exp.employee_id.name))
            ctx = dict(self.env.context or {})
            ctx.update({
                # 'default_sale_id': petty.id,
                'default_employee_id': exp.employee_id.id,
                'default_amount': amount,
                'default_expense_sheet_id': exp.id,
                'default_currency_id':exp.currency_id.id,
                'default_partner_id': partner_id,
            })
            return {
                'name': _('Add Payment To Petty Cash'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'petty.pay.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }