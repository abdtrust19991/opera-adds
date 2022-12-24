# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from lxml import etree

from odoo import tools
from odoo import api, models,fields,exceptions,_


class PayWizard(models.TransientModel):
    _name = 'close.advances'


    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True,domain="[('adv_pay_close','=',True)]" )
    remaining = fields.Float(string="Amount",  required=True,readonly=True  )
    advance_ids = fields.Many2many(comodel_name="advance.salary", relation="",  string="",readonly=True )
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, ondelete='cascade')

    def close_advances(self):
        for rec in self.advance_ids:
            partner = self.env['res.partner']
            account_move_obj = self.env['account.move']
            employee = rec.employee_id
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
            if not rec.advance_type.credit_account_id:
                raise exceptions.ValidationError("Credit Account Can't Be Null")

            price = rec.remaining
            vals = []
            if price:
                vals.append((0, 0, {'name': 'Loan# ' + rec.name,
                                    'partner_id': partner.id,
                                    'account_id': debit_account,
                                    'debit': price,
                                    'credit': 0.0}))
                vals.append((0, 0, {'name': 'Loan# ' + rec.name,
                                    'partner_id': partner.id,
                                    'account_id': rec.advance_type.credit_account_id.id,
                                    'debit': 0.0,
                                    'credit': price}))

            move = account_move_obj.create(
                {'ref': 'Loan# ' + rec.name, 'journal_id': self.journal_id.id, 'line_ids': vals})
            print("move ==> ", move)
            move.action_post()
            rec.paid_amount += rec.remaining
            rec._compute_remaining()
            if rec.remaining == 0.0:
                rec.state = 'close'
                rec.post_date = fields.Date.today()
                rec.close_date = fields.Date.today()




