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
# from werkzeug import url_encode
from werkzeug import urls
from werkzeug.urls import url_encode

import logging

LOGGER = logging.getLogger(__name__)

import time
import babel
import math

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class PettyPayWizard(models.TransientModel):
    _name = 'petty.pay.wizard'

    petty_id = fields.Many2one('petty.cash', 'Petty Cash')
    petty_cash_ids = fields.Many2many(comodel_name="petty.cash",  string="Petty Cash", )

    journal_id = fields.Many2one('account.journal', string='Payment Method',compute="_compute_journal_and_balance",)
    expense_sheet_id = fields.Many2one(comodel_name='hr.expense.sheet', string='Expense Sheet')
    partner_id = fields.Many2one('res.partner', string='Partner')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
                                         help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    balance = fields.Monetary(string='Balance', compute="_compute_journal_and_balance",)
    date = fields.Date(defualt=fields.Date.today)
    communication = fields.Char(string='Memo')

    @api.depends('petty_cash_ids')
    def _compute_journal_and_balance(self):
        self.ensure_one()
        if self.petty_cash_ids:
            journal = self.petty_cash_ids[0].journal_id.id
            total_balance = 0.0
            for rec in self.petty_cash_ids:
                if rec.journal_id.id != journal:
                    raise ValidationError(_('The journals of Petty Cash id deterrent'))
                total_balance += rec.balance
            self.journal_id = journal
            self.balance = total_balance
        else:
            self.journal_id = None
            self.balance = 0

    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        self.ensure_one()
        if not self.journal_id:
            self.hide_payment_method = True
            return
        journal_payment_methods = self.journal_id.outbound_payment_method_ids
        self.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

   # Change Payment Method Domain
    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            return {
                'domain': {'payment_method_id': [('payment_type', '=', 'outbound')]}}
                # 'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        lst=[]
        res={}
        petty_ids = self.env['petty.cash'].search([('employee_id', '=', self.employee_id.id),('state', '=', 'paid')])
        for rec in petty_ids:
            if rec.balance > 0.0 :
                lst.append(rec.id)
        res.update({
            'domain': {
                'petty_cash_ids': [('id', '=', list(set(lst)))],

            }
        })
        return res

    def action_post(self):
        for pay in self:
            # if pay.amount> pay.balance:
            #     raise ValidationError(_('You Cannot Exceed Employee Balance '))
            if pay.expense_sheet_id:
                expense_id = pay.expense_sheet_id
                print("expense_id == ",expense_id)
                domain = [('partner_id', '=', pay.partner_id.id),('move_id','=',expense_id.account_move_id.id),
                          ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                          ('amount_residual_currency', '!=', 0.0)]
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                lines = self.env['account.move.line'].search(domain)
                LOGGER.info('move lines %s' % lines)
                petty=self.petty_id
                LOGGER.info('petty %s' % petty)
                petty.register_payment(lines)
                LOGGER.info('petty after register payment')
                petty_line = self.env['petty.cash.line'].create({
                    'name':expense_id.name,
                    'amount':pay.amount,
                    'petty_id':petty.id,
                    'expense_sheet_id': expense_id.id,
                    'payment_id': pay.id,

                })
                LOGGER.info('petty line created %s' % petty_line)

    def _get_payment_vals(self):
        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.journal_id.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date': self.date,
            # 'communication': self.communication
        }

    def petty_expense_post_payment(self):
        self.ensure_one()
        max_petty_date = max(self.petty_cash_ids.mapped('date'))
        if max_petty_date:
            if max_petty_date > self.date:
                raise ValidationError(_('You can not pay from petty cash before being paid!'))
        # if self.amount > self.balance:
        #     raise ValidationError(_('You Cannot Exceed Employee Balance '))
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        # expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)
        expense_sheet = self.expense_sheet_id

        if self.amount >expense_sheet.rem_amount:
            msg = 'You Cannot Pay Amount Greater Than Expense Sheet Amount \n' \
                  'The Open Amount = %s ' % (expense_sheet.rem_amount)
            raise UserError(_('Amount Over Limits !\n' + msg))

        expense_sheet.paid_amount += self.amount
        # Create payment and post it
        payment = self.env['account.payment'].create(self._get_payment_vals())
        payment.action_post()
        # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        payment.line_ids.sudo().write({'petty_id':self.petty_id.id})
        for line in payment.line_ids + expense_sheet.account_move_id.line_ids:
            if line.account_id.internal_type == 'payable':
                account_move_lines_to_reconcile |= line
        account_move_lines_to_reconcile.reconcile()
        inv_amount=payment.amount

        remaining_amount = self.amount
        for petty in self.petty_cash_ids[:-1]:
            petty_paid_amount = min(petty.balance , remaining_amount)
            self.env['petty.cash.line'].create({
                'name': expense_sheet.name,
                'amount': petty_paid_amount,
                'petty_id': petty.id,
                'expense_sheet_id': expense_sheet.id,
                'payment_id': payment.id,
            })
            if petty.balance == 0.0:
                petty.state = 'adjust'
            remaining_amount -= petty_paid_amount
            if remaining_amount <= 0:
                break

        last_petty = self.petty_cash_ids[-1]
        if remaining_amount > 0.0 and last_petty:
            self.env['petty.cash.line'].create({
                'name': expense_sheet.name,
                'amount': remaining_amount,
                'petty_id': last_petty.id,
                'expense_sheet_id': expense_sheet.id,
                'payment_id': payment.id,
            })
            if last_petty.balance == 0.0:
                last_petty.state = 'adjust'

        # balance=0.0
        # for rec in self.petty_cash_ids:
        #
        #     x= len(self.petty_cash_ids.ids) -1
        #     last_rec=self.petty_cash_ids[x]
        #     if inv_amount >= rec.balance:
        #         inv_amount =inv_amount - rec.balance
        #         if rec.id==last_rec.id:
        #             balance = inv_amount * -1
        #
        #         rec.sudo().write({'balance2':balance})
        #
        #     else:
        #
        #         balance=rec.balance - inv_amount
        #         rec.sudo().write({'balance2':balance})
        #         self.env['petty.cash.line'].create({
        #             'name': expense_sheet.name,
        #             'amount': payment.amount,
        #             'petty_id': rec.id
        #
        #         })
        #         break
        #     self.env['petty.cash.line'].create({
        #         'name': expense_sheet.name,
        #         'amount': payment.amount,
        #         'petty_id': rec.id
        #
        #     })
        body = (_("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made.") % (payment.amount, payment.currency_id.symbol, url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, expense_sheet.name))
        expense_sheet.message_post(body=body)
        return {'type': 'ir.actions.act_window_close'}


class PettyPayInvoiceWizard(models.TransientModel):
    _name = 'petty.pay.invoice.wizard'

    petty_id = fields.Many2one('petty.cash', 'Petty Cash')
    petty_cash_ids = fields.Many2many(comodel_name="petty.cash", string="Petty Cash", )

    journal_id = fields.Many2one('account.journal', string='Payment Method',compute="_compute_journal_and_balance",readonly=True)
    invoice_id = fields.Many2one(comodel_name='account.move', string='Invoice')
    partner_id = fields.Many2one('res.partner', string='Partner')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
                                         help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    balance = fields.Monetary(string='Balance', compute="_compute_journal_and_balance")
    communication = fields.Char(string='Memo')
    date = fields.Date(required=False,defualt=fields.Date.today )

    @api.depends('petty_cash_ids')
    def _compute_journal_and_balance(self):
        self.ensure_one()
        if self.petty_cash_ids:
            journal=self.petty_cash_ids[0].journal_id.id
            total_balance=0.0
            for rec in self.petty_cash_ids:
                if rec.journal_id.id != journal:
                    raise ValidationError(_('The journals of Petty Cash id deterrent'))
                total_balance += rec.balance
            self.journal_id = journal
            self.balance = total_balance
        else:
            self.journal_id = None
            self.balance = 0

    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        self.ensure_one()
        if not self.journal_id:
            self.hide_payment_method = True
            return
        journal_payment_methods = self.journal_id.outbound_payment_method_ids
        self.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            return {
                'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        lst = []
        res = {}
        petty_ids = self.env['petty.cash'].search([('employee_id', '=', self.employee_id.id),('state','=','paid')])
        for rec in petty_ids:
            if rec.balance > 0.0:
                lst.append(rec.id)
        res.update({
            'domain': {
                'petty_cash_ids': [('id', '=', list(set(lst)))],
            }
        })
        return res



    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     employee_id=False
    #     if self.partner_id:
    #         employee_ids=self.env['hr.employee'].search([('address_home_id','=',self.partner_id.id)])
    #         if employee_ids:
    #             employee_id=employee_ids[0].id
    #
    #     return {'domain': {'petty_id': [('employee_id', '=', employee_id)]}}

    def _get_payment_vals(self):
        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.invoice_id.partner_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.journal_id.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': self.amount,
            'reconciled_invoice_ids': [(4, self.invoice_id.id, None)],
            'currency_id': self.currency_id.id,
            'date': self.date,
            # 'communication': self.communication
        }
        # available_partner_bank_accounts = self.partner_id.bank_ids
        # partner_bank_id = available_partner_bank_accounts[0]._origin if available_partner_bank_accounts else False
        # return {
        #     'date': self.date,
        #     'amount': self.amount,
        #     'payment_type': 'outbound',
        #     'partner_type': 'supplier',
        #     'journal_id': self.journal_id.id,
        #     'currency_id': self.currency_id.id,
        #     'partner_id': self.partner_id.id,
        #     'partner_bank_id': partner_bank_id,
        #     'payment_method_id': self.payment_method_id.id,
        #     'destination_account_id': self.invoice_id.mapped('invoice_line_ids')[0].account_id.id,
        # }

    def petty_invoice_post_payment(self):
        self.ensure_one()
        max_petty_date = max(self.petty_cash_ids.mapped('date'))
        if max_petty_date:
            if max_petty_date > self.date:
                raise ValidationError(_('You can not pay from petty cash before being paid!'))
        inv_amount=self.amount
        balance=0.0
        # if self.amount > self.balance:
        #     raise ValidationError(_('You Cannot Exceed Employee Balance '))
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        invoice = self.invoice_id

        if self.amount > self.invoice_id.amount_residual:
            msg = 'You Cannot Pay Amount Greater Than Invoice Amount \nThe Open Amount = %s ' %(invoice.amount_residual)
            raise UserError(_('Amount Over Limits !\n' + msg))

            # raise ValidationError(_('You Cannot Pay Amount Greater Than Invoice Amount! '))

        partner = invoice.partner_id
        # Create payment and post it

        payments = self.env['account.payment.register'].with_context(active_model='account.move',
                                                                     active_ids=active_ids).create({
            'amount': self.amount,
            'group_payment': True,
            'journal_id': self.journal_id.id,
            'payment_difference_handling': 'open',
            'payment_method_id': self.payment_method_id.id,
            'currency_id': self.currency_id.id,
        })._create_payments()

        # payment = self.env['account.payment'].sudo().create(self._get_payment_vals())

        # payment.action_post()
        # for move_line in payment.line_ids:
        #     move_line.sudo().write({'petty_cash_ids': self.petty_cash_ids.ids})
        # #     if move_line.account_id.id not in [partner.property_account_payable_id.id,partner.property_account_receivable_id.id]:
        # #         move_line.write({'partner_id': self.invoice_id.employee_id.address_home_id.id})

        remaining_amount = self.amount
        for petty in self.petty_cash_ids[:-1]:
            petty_paid_amount = min(petty.balance , remaining_amount)
            self.env['petty.cash.line'].create({
                'name': invoice.name,
                'amount': petty_paid_amount,
                'petty_id': petty.id,
                'invoice_id': invoice.id,
                'payment_id': payments.id,
            })
            if petty.balance == 0.0:
                petty.state = 'adjust'
            remaining_amount -= petty_paid_amount
            if remaining_amount <= 0:
                break

        last_petty = self.petty_cash_ids[-1]
        if remaining_amount > 0.0 and last_petty:
            self.env['petty.cash.line'].create({
                'name': invoice.name,
                'amount': remaining_amount,
                'petty_id': last_petty.id,
                'invoice_id': invoice.id,
                'payment_id': payments.id,
            })
            if last_petty.balance == 0.0:
                last_petty.state = 'adjust'


        # for rec in self.petty_cash_ids:
        #     x = len(self.petty_cash_ids.ids) -1
        #     last_rec = self.petty_cash_ids[x]
        #     if inv_amount >= rec.balance:
        #         inv_amount = inv_amount - rec.balance
        #
        #         if rec.id==last_rec.id:
        #             balance = inv_amount * -1
        #
        #         rec.sudo().write({'balance2':balance})
        #
        #     else:
        #
        #         balance = rec.balance - inv_amount
        #         rec.sudo().write({'balance2':balance})
        #         self.env['petty.cash.line'].create({
        #             'name': invoice.number,
        #             'amount': payment.amount,
        #             'petty_id': rec.id
        #
        #         })
        #         break
        #     self.env['petty.cash.line'].create({
        #             'name': invoice.number,
        #             'amount': payment.amount,
        #             'petty_id': rec.id
        #
        #         })



        return {'type': 'ir.actions.act_window_close'}





