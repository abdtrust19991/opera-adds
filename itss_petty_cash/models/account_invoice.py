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


class AccountInvoice(models.Model):

    _inherit = "account.move"

    employee_id = fields.Many2one(comodel_name="hr.employee",string="Responsible Employee" )

    def petty_inv_pay(self):
        for inv in self:
            view = self.env.ref('itss_petty_cash.petty_pay_invoice_wizard_from_view')
            # amount = inv.amount_total
            amount=inv.amount_residual
            partner_id = inv.partner_id
            # employee_ids = self.env['hr.employee'].search([('address_home_id', '=', partner_id.id)])
            if not self.employee_id :
                raise ValidationError(_('You Should Specify Responsible Employee!'))
            if not self.employee_id.address_home_id:
                raise ValidationError(_('Responsible Employee must have home address!'))

            employee_id=self.employee_id
            ctx = dict(self.env.context or {})
            ctx.update({
                # 'default_sale_id': petty.id,
                'default_employee_id': employee_id.id,
                'default_amount': amount,
                # 'default_move_id': inv.id,
                'default_invoice_id': inv.id,
                'default_currency_id':inv.currency_id.id,
                'default_partner_id': employee_id.address_home_id.id,
                # 'default_partner_id': self.partner_id.id,
            })
            print('the ctx is',ctx)
            return {
                'name': _('Pay With Petty Cash'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'petty.pay.invoice.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }