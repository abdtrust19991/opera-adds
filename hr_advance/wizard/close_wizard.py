# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from lxml import etree

from odoo import tools
from odoo import api, models,fields,exceptions,_


class PayWizard(models.TransientModel):
    _name = 'close.wizard'

    advance_id = fields.Many2one(comodel_name="advance.salary", string="Advance Salary", required=True, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, related='advance_id.employee_id')
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True,domain="[('adv_pay_close','=',True)]" )
    remaining = fields.Float(string="Amount",  required=True, )
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, ondelete='cascade')
    close_date = fields.Date(string="", default=lambda self: fields.Datetime.now(), required=True, )

    @api.onchange('advance_id')
    def onchange_advance_id(self):
        if self.advance_id:
            self.remaining= self.advance_id.remaining

    @api.constrains('remaining')
    def _check_date(self):
        if self.remaining > self.advance_id.remaining:
            raise exceptions.ValidationError(_('The Amount must not be grater than  advance remaining amount'))
        if self.remaining == 0.0:
            raise exceptions.ValidationError(_('The Amount must not be = 0.0'))

    def action_close(self):
        partner = self.env['res.partner']
        account_move_obj = self.env['account.move']
        employee = self.employee_id
        if employee.address_home_id:
            partner = employee.address_home_id

        elif employee.user_id:
            partner = employee.user_id.partner_id
        else:
            raise exceptions.ValidationError("The Employee Doesn't Have Partner")
        if self.journal_id.type == 'bank':
            debit_account = self.journal_id.payment_debit_account_id
        else:
            debit_account = self.journal_id.default_account_id
        if not debit_account:
            raise exceptions.ValidationError("Debit Account Can't Be Null")
        if not self.advance_id.advance_type.credit_account_id:
            raise exceptions.ValidationError("Credit Account Can't Be Null")

        price = self.remaining
        vals = []
        if price:
            vals.append((0, 0, {'name': 'Loan# ' + self.advance_id.name,
                                'partner_id': partner.id,
                                'account_id': debit_account.id,
                                'debit': price,
                                'credit': 0.0}))
            vals.append((0, 0, {'name': 'Loan# ' + self.advance_id.name,
                                'partner_id': partner.id,
                                'account_id':  self.advance_id.advance_type.credit_account_id.id,
                                'debit': 0.0,
                                'credit': price}))

        move = account_move_obj.create(
            {'ref': 'Loan# ' + self.advance_id.name, 'journal_id': self.journal_id.id, 'line_ids': vals})
        print("move ==> ", move)
        move.action_post()
        self.advance_id.paid_amount += self.remaining
        self.advance_id._compute_remaining()
        if self.advance_id.remaining == 0.0:
            self.advance_id.state = 'close'
            self.advance_id.post_date = fields.Date.today()
            self.advance_id.close_date = self.close_date


