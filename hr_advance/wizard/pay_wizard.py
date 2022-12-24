# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from lxml import etree

from odoo import tools
from odoo import api, models,fields,exceptions


class PayWizard(models.TransientModel):
    _name = 'pay.wizard'

    advance_id = fields.Many2one(comodel_name="advance.salary", string="Advance Salary", required=True, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, related='advance_id.employee_id')
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True,domain="[('adv_pay_close','=',True)]" )
    remaining = fields.Float(string="Amount",related='advance_id.remaining' )
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, ondelete='cascade')
    payment_date = fields.Date(string="", default=lambda self: fields.Datetime.now(), required=True, )

    def action_pay(self):
        partner = self.env['res.partner']
        account_move_obj=self.env['account.move']
        currency_id = self.company_id.currency_id
        if self.employee_id.address_home_id:
            partner = self.employee_id.address_home_id

        elif self.employee_id.user_id:
            partner = self.employee_id.user_id.partner_id
        else:
            raise exceptions.ValidationError("The Employee Doesn't Have Partner")

        if self.journal_id.type == 'bank':
            credit_account = self.journal_id.payment_credit_account_id
        else:credit_account = self.journal_id.default_account_id

        if not self.advance_id.advance_type.debit_account_id:
            raise exceptions.ValidationError("Debit Account Can't Be Null")
        if not credit_account:
            raise exceptions.ValidationError("Credit Account Can't Be Null")

        vals = []

        price = self.remaining
        if price:
            vals.append((0, 0, {'name': 'Loan# ' + self.advance_id.name,
                                'partner_id': partner.id,
                                'account_id': self.advance_id.advance_type.debit_account_id.id,
                                'debit': price,
                                'credit': 0.0}))
            vals.append((0, 0, {'name': 'Loan# ' + self.advance_id.name,
                                'partner_id': partner.id,
                                'account_id': credit_account.id,
                                'debit': 0.0,
                                'credit': price}))

        move = account_move_obj.create(
            {'ref': 'Loan# ' + self.advance_id.name, 'journal_id': self.journal_id.id,'line_ids': vals})
        print("move ==> ",move)
        move.action_post()
        self.advance_id.state = 'paid'

        self.advance_id.payment_date = self.payment_date



