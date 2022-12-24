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


from odoo import models, fields, api, tools, _
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

import time
import babel
import math

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class PettyCashType(models.Model):
    _name = 'petty.cash.type'

    _description = 'Petty Cash Types'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')], string='State',
        copy=False, default='draft', tracking=True)

    type = fields.Selection([
        ('temp', 'Temporary'),
        ('per', 'Permanent')], string='Type',
        copy=False, default='temp')

    name = fields.Char(
        'name', copy=False)
    journal_id = fields.Many2one(comodel_name='account.journal',
                                 string='Petty Cash Journal')
    # debit_account_id = fields.Many2one(
    #     'account.account',
    #     'Petty Cash Debit Account'
    # )
    # credit_account_id = fields.Many2one(
    #     'account.account',
    #     'Petty Cash Credit Account'
    # )
    reference = fields.Char('Reference')
    date = fields.Date('Payment Date')
    adj_date = fields.Date('Adjustment Date')
    force_date = fields.Boolean('Force Adjustment Date')
    move_group = fields.Boolean('Group Journal Entries')

    def unlink(self):
        if self.env['petty.cash'].search([('type_id', 'in', self.ids)], limit=1):
            raise UserError(_('You cannot delete Petty Cash type that has been used in petty cash before'))
        return super(PettyCashType, self).unlink()

    def action_confirm(self):

        self.write({'state': 'confirm'})
        return True

    def action_draft(self):
        if self.env['petty.cash'].search([('type_id', 'in', self.ids)], limit=1):
            raise UserError(_('You cannot Set To Draft Petty Cash type that has been used in petty cash before'))
        self.write({'state': 'draft'})
        return True


class PettyCash(models.Model):
    _name = 'petty.cash'
    _description = 'Employees Petty Cash'
    _inherit = ['mail.thread']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid'), ('reconciled', 'Reconciled'),('adjust', 'Adjusted')], string='State',
        copy=False, default='draft', tracking=True)

    name = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'))
    type_id = fields.Many2one(comodel_name='petty.cash.type', string='Petty Cash Type',
                              domain="[('state', '=', 'confirm')]")

    amount = fields.Monetary('Amount')
    account_move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)
    line_ids = fields.One2many(comodel_name='petty.cash.line', inverse_name='petty_id', string='Lines')

    remain_amount = fields.Monetary('Remaining Amount')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee To assign', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    date = fields.Date('Payment Date')
    adj_date = fields.Date('Adjustment Date')
    journal_id = fields.Many2one(comodel_name='account.journal', string='Petty Cash Journal')
    # debit_account_id = fields.Many2one(
    #     'account.account',
    #     'Petty Debit Cash Account'
    # )
    # credit_account_id = fields.Many2one(
    #     'account.account',
    #     'Petty Cash Credit Account'
    # )
    pay_journal_id = fields.Many2one(comodel_name='account.journal', string='Payment Journal',
                                     domain=[('type', 'in', ['cash', 'bank'])])
    reference = fields.Char('Reference')
    payment_ids = fields.Many2many(comodel_name='account.payment', string='Payments', copy=False)
    payment_count = fields.Integer(string='# of Payments', compute='_get_payment', readonly=True, copy=False)
    paid = fields.Boolean(string='Is Paid', compute='_compute_paid')
    balance = fields.Monetary('Balance',readonly=True,compute='_compute_amount_balance')
    balance2 = fields.Monetary('Balance value',readonly=True,)

    def register_payment(self, payment_line):
        line_to_reconcile = self.env['account.move.line']
        for petty in self:
            line_to_reconcile += petty.account_move_id.line_ids.filtered(
                lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
        return (line_to_reconcile + payment_line).reconcile()

    @api.constrains('amount')
    def _check_amount(self):
        for petty in self:
            if petty.amount <= 0:
                raise ValidationError(_('Petty cash amount must be more than 0'))

    def get_employee_balance2(self):
        account_move_line_obj = self.env['account.move.line']
        for petty in self:
            balance = 0
            partner_id = petty._get_partner_id()
            move_lines = account_move_line_obj.search([('partner_id', '=', partner_id),
                                                       ('account_id', 'in',
                                                        [petty.journal_id.default_account_id.id,
                                                         petty.journal_id.default_account_id.id]),
                                                       ('balance', '!=', 0),
                                                       ])
            # if move_lines:

                # for rec in move_lines:
                #     print("rec.petty_cash_ids >>> = ",rec.petty_cash_ids)
                #     if rec.petty_cash_ids:
                #         print(rec.petty_cash_ids)
                #         if petty.id in rec.petty_cash_ids:
                #             balance +=rec.balance
            paid = sum([l.amount for l in petty.line_ids])
            # petty.balance = balance

    @api.depends('payment_ids')
    def _compute_paid(self):
        for petty in self:
            paid_amount = sum([p.amount for p in petty.payment_ids])
            if paid_amount >= petty.amount:
                # petty.write({'state': 'paid'})
                petty.paid = True

    @api.depends('payment_ids')
    def _get_payment(self):
        for petty in self:
            petty.payment_count = len(petty.payment_ids.ids)
            paid_amount = sum([p.amount for p in petty.payment_ids])
            # print('pai amount is',paid_amount)
            # if paid_amount >=petty.amount:
            #     print('thestate will be paid')
            #     petty.write({'state':'paid'})

    def action_register_petty_payment2(self):
        # this method is from the petty cash journal and the employee payable account
        for petty in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = petty.date
            name = _('Petty Cash of %s') % (petty.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': petty.name,
                'journal_id': petty.journal_id.id,
                'date': date,
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = petty.amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = petty._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    petty.employee_id.name))
            credit_account_id = petty.journal_id.default_account_id.id
            debit_account_id = petty.employee_id.address_home_id.property_account_payable_id.id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': petty.journal_id.id,
                    'petty_id': petty.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': credit_account_id,
                    'journal_id': petty.journal_id.id,
                    'petty_id': petty.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            petty.write({'account_move_id': move.id})
            move.post()
        self.write({'state': 'paid'})
        return True

    def action_register_petty_payment(self):
        for petty in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = petty.date
            name = _('Petty Cash of %s') % (petty.employee_id.name)
            pay_journal = petty.pay_journal_id
            move_dict = {
                'narration': name,
                'ref': petty.name,
                'journal_id': petty.pay_journal_id.id,
                'date': date,
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = petty.amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = petty._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    petty.employee_id.name))
            debit_account_id = petty.journal_id.default_account_id.id
            credit_account_id = petty.pay_journal_id.default_account_id.id

            # create payment
            payment_methods = (
                                          amount < 0) and pay_journal.outbound_payment_method_ids or pay_journal.inbound_payment_method_ids
            journal_currency = pay_journal.currency_id or pay_journal.company_id.currency_id
            # payment = self.env['account.payment'].create({
            #     'payment_method_id': payment_methods and payment_methods[0].id or False,
            #     'payment_type': amount < 0 and 'outbound' or 'inbound',
            #     'partner_id': partner_id,
            #     'partner_type': 'supplier',
            #     'journal_id': pay_journal.id,
            #     'date': date,
            #     'state': 'reconciled',
            #     'currency_id': journal_currency.id,
            #     'amount': abs(amount),
            #     'name': petty.name,
            # })
            # payment_id = payment.id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': pay_journal.id,
                    'petty_id': petty.id,

                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': credit_account_id,
                    'journal_id': pay_journal.id,
                    'petty_id': petty.id,
                    # 'payment_id': payment_id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            petty.write({'account_move_id': move.id})
            move.post()
        self.write({'state': 'paid'})
        return True

    def action_post(self):
        for petty in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = petty.date
            name = _('Petty Cash of %s') % (petty.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': petty.name,
                'journal_id': petty.journal_id.id,
                'date': date,
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = petty.amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = petty._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    petty.employee_id.name))
            debit_account_id = petty.journal_id.default_account_id.id
            credit_account_id = petty.employee_id.address_home_id.property_account_payable_id.id
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': petty.journal_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': credit_account_id,
                    'journal_id': petty.journal_id.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            petty.write({'account_move_id': move.id})
            move.post()
        self.write({'state': 'post'})
        return True


    def action_approve(self):
        self.write({'state': 'approved'})
        return True


    def action_draft(self):
        self.write({'state': 'draft'})
        return True


    def action_paid(self):
        return self.write({'state': 'paid'})

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            new_name = self.env['ir.sequence'].next_by_code('petty.cash') or _('New')
            values['name'] = new_name
            # values['balance'] = values['amount']
        petty = super(PettyCash, self).create(values)

        return petty

    # @api.depends('amount','balance2','line_ids','state')
    @api.depends('amount','line_ids','state')
    def _compute_amount_balance(self):
        for rec in self:
            if rec.state in ['paid','adjust']:
                rec.balance = rec.amount - sum([line.amount for line in rec.line_ids])
            else:
                rec.balance = 0
        print("** balance ** ")
        # if not self.line_ids and self.state != 'adjust':
        #
        #     self.balance = self.amount
        #     print("** balance 1 ** ", self.balance)
        #     print("** balance2 1 ** ", self.balance2)
        # elif self.state == 'adjust':
        #     self.balance= self.amount - self.balance2
        #     print("** balance 2 ** ", self.balance)
        #     print("** balance2 2 ** ", self.balance2)
        # else:
        #     self.balance = self.balance2
        #     print("** balance 1  55** ", self.balance)
        #     print("** balance2 1 55** ", self.balance2)
        # pass
    # @api.onchange('amount')
    # def onchange_method(self):
    #     print('amount 11=',self.amount)
    #     print('balance 11=',self.balance)
    #     # self.write({'balance': self.amount})
    #     self.balance = self.amount
    #     print('balance 12=', self.balance)
    #
    #
    # def write(self, values):
    #     print('yyyy ',values)
    #     if 'amount' in values:
    #         self.balance==values['amount']
    #
    #     return super(PettyCash, self).write(values)

    @api.onchange('type_id')
    def onchange_type(self):
        if self.type_id:
            self.journal_id = self.type_id.journal_id
            # self.debit_account_id = self.type_id.debit_account_id
            # self.credit_account_id = self.type_id.credit_account_id
            self.adj_date = self.type_id.adj_date

    def _get_partner_id(self):
        for ptt in self:
            partner_id = False
            if ptt.employee_id.address_home_id:
                partner_id = ptt.employee_id.address_home_id.id
            elif ptt.employee_id.user_id:
                partner_id = ptt.employee_id.user_id.partner_id.id
            return partner_id


    def action_view_payment(self):

        payments = self.mapped('payment_ids')
        action = self.env.ref('account.action_account_payments').read()[0]
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = payments.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def petty_register_payment(self):
        for petty in self:
            view = self.env.ref('itss_petty_cash.view_account_payment_petty_cash_form')
            amount = petty.amount
            partner_id = petty._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    petty.employee_id.name))
            if petty.payment_ids:
                for pay in petty.payment_ids:
                    if pay.state == 'approved':
                        amount = amount - pay.amount

            context = "{'search_default_customer':1, 'show_address': 1}"
            ctx = dict(self.env.context or {})
            ctx.update({
                # 'default_sale_id': petty.id,
                'default_amount': amount,
                'default_communication': petty.name,
                'default_payment_type': 'outbound',
                'default_partner_type': 'supplier',
                'default_journal_id': petty.journal_id.id,
                'default_partner_id': partner_id,
                'default_petty_id': petty.id
            })
            return {
                'name': _('Add Payment To Petty Cash'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                # 'res_id': payment.id,
                'context': ctx,
            }


class PettyCashLine(models.Model):
    _name = 'petty.cash.line'

    name = fields.Char('Reference')
    amount = fields.Monetary('Amount')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    petty_id = fields.Many2one(comodel_name='petty.cash', string='Petty Cash')
    invoice_id = fields.Many2one(comodel_name='account.move')
    expense_sheet_id = fields.Many2one(comodel_name='hr.expense.sheet')
    petty_adj_id = fields.Many2one(comodel_name='petty.cash.adj')
    payment_id = fields.Many2one(comodel_name='account.payment')


class PettyCashAdjustment(models.Model):
    _name = 'petty.cash.adj'
    _description = 'Employees Petty Cash Adjustment'
    _inherit = ['mail.thread']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid'), ('reconciled', 'Reconciled')], string='State',
        copy=False, default='draft', tracking=True)

    name = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'))

    petty_id = fields.Many2one(comodel_name='petty.cash', string='Petty Cash')
    type_id = fields.Many2one(related='petty_id.type_id', string='Petty Cash Type', store=True, readonly=1)
    journal_id = fields.Many2one(comodel_name='account.journal', related='petty_id.journal_id', store=True,
                                 readonly=True, string='Petty Cash Journal')
    # debit_account_id = fields.Many2one(
    #     'account.account',
    #     'Petty Debit Cash Account',
    #     related='petty_id.debit_account_id', store=True,
    #     readonly=True,
    # )
    # credit_account_id = fields.Many2one(
    #     'account.account',
    #     'Petty Cash Credit Account',
    #     related='petty_id.credit_account_id', store=True,
    #     readonly=True,
    # )
    pay_journal_id = fields.Many2one(comodel_name='account.journal', string='Payment Journal',
                                     domain=[('type', 'in', ['cash', 'bank'])])
    # amount = fields.Monetary('Amount', compute='compute_amount')
    amount = fields.Monetary('Amount')
    # remain_amount = fields.Monetary('Remaining Amount')
    # adjustment_amount = fields.Monetary('Adjustment Amount')
    date = fields.Date('Payment Date')
    account_move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)

    adj_date = fields.Date('Adjustment Date')
    employee_id = fields.Many2one(comodel_name='hr.employee', related='petty_id.employee_id', store=True, readonly=True,
                                  string='Employee To assign')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    # @api.depends('type_id.type')
    # def compute_amount(self):
    #     for adj in self:
    #         print('iam in compute amount')
    #         if adj.type_id:
    #             if adj.type_id.type == 'temp':
    #                 adj.amount = -adj.petty_id.balance
    #             if adj.type_id.type == 'per':
    #                 adj.amount = adj.petty_id.amount - adj.petty_id.balance

    @api.onchange('petty_id')
    def onchange_type(self):
        petty_id = self.petty_id
        if self.petty_id:
            type_id = petty_id.type_id
            amount = 0
            if type_id and petty_id:
                if type_id.type == 'temp':
                    amount = -petty_id.balance
                if type_id.type == 'per':
                    amount = petty_id.amount - petty_id.balance
                self.update({'amount': amount})



    def action_approve(self):
        self.write({'state': 'approved'})
        return True


    def action_draft(self):
        self.write({'state': 'draft'})
        return True


    def action_paid(self):
        return self.write({'state': 'paid'})

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            new_name = self.env['ir.sequence'].next_by_code('petty.cash.adj') or _('New')
            values['name'] = new_name
        petty = super(PettyCashAdjustment, self).create(values)
        return petty

    def _get_partner_id(self):
        for ptt in self:
            partner_id = False
            if ptt.employee_id.address_home_id:
                partner_id = ptt.employee_id.address_home_id.id
            elif ptt.employee_id.user_id:
                partner_id = ptt.employee_id.user_id.partner_id.id
            return partner_id

    def action_register_petty_adj_payment(self):
        for adj in self:
            line_ids = []
            date = adj.date
            name = _('Petty Cash Adjustment of %s') % (adj.petty_id.name)
            pay_journal = adj.pay_journal_id
            move_dict = {
                'narration': name,
                'ref': adj.name,
                'journal_id': adj.pay_journal_id.id,
                'date': date,
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = adj.amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = adj._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    adj.employee_id.name))
            if adj.petty_id.balance > 0 and (adj.petty_id.balance + adj.amount) < 0:
                raise ValidationError(_('You Cannot Exceed Employee Balance '))

            debit_account_id = adj.journal_id.default_account_id.id
            credit_account_id = adj.pay_journal_id.default_account_id.id

            # create payment
            payment_methods = (amount < 0) and pay_journal.outbound_payment_method_ids or pay_journal.inbound_payment_method_ids
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': adj.name,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': pay_journal.id,
                    'petty_id': adj.petty_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': adj.name,
                    'partner_id': partner_id,
                    'account_id': credit_account_id,
                    'journal_id': pay_journal.id,
                    'petty_id': adj.petty_id.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            account_move_lines_to_reconcile = self.env['account.move.line']
            # for line in move.line_ids + adj.petty_id.account_move_id.line_ids:
            #     if line.account_id.internal_type == 'payable':
            #         print('account line reconicile state', line.name, line.reconciled)
            #         account_move_lines_to_reconcile |= line
            # print('moves to reconcile is', account_move_lines_to_reconcile)
            # account_move_lines_to_reconcile.reconcile()
            adj.write({'account_move_id': move.id})
            move.post()

            # adj.petty_id.write({'balance2': adj.petty_id.balance2 + adj.amount})
            adj.env['petty.cash.line'].create({
                'name': adj.name,
                'amount': -adj.amount,
                'petty_id': adj.petty_id.id,
                'petty_adj_id': adj.id,

            })
            if float_is_zero(adj.petty_id.balance,precision_digits=precision):
                adj.petty_id.write({'state': 'adjust'})
            adj.write({'state': 'paid'})

        return True
