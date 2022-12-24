# -*- coding: utf-8 -*-

from odoo import api, fields, models, _,exceptions
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
class advance_salary_type(models.Model):
    _name = 'advance.salary.type'
    name = fields.Char(string="Name", required=True, )

    debit_account_id = fields.Many2one('account.account', string="Debit Account", required=True,)
    credit_account_id = fields.Many2one('account.account', string="Credit Account", required=True,)




class advance_salary(models.Model):
    _name = 'advance.salary'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char()
    employee_id = fields.Many2one(comodel_name="hr.employee",

                                  tracking=True,string="Employee", required=False, )
    advance_type = fields.Many2one(comodel_name="advance.salary.type", tracking=True, string="Advance Type", required=True, )
    create_date = fields.Date(string="Create Date", required=False, )
    post_date = fields.Date(string="Post Date", tracking=True, required=False, )
    due_date = fields.Date(string="Due Date",tracking=True, required=False, )

    amount = fields.Float(string="Amount", tracking=True, required=False, )
    remaining = fields.Float(string="Remaining Amount",tracking=True,  required=False,compute="_compute_remaining",store=True )
    paid_amount = fields.Float(string="Paid Amount",  tracking=True,required=False,readonly=True )
    on_salary = fields.Boolean(string="Deduct From Salary",tracking=True, )
    num_install = fields.Integer(string="Installment Number",  required=False, )
    install_value = fields.Float(string="Installment Value", required=False,compute="_compute_install_value" )
    commission = fields.Float(string="Commission", required=False, )
    installment_ids = fields.One2many(comodel_name="pay.advance.line", inverse_name="advance_id", string="Installment Lines", required=False, )
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, store=True)

    count_journal = fields.Integer(string="Journal Count",  required=False,compute="_compute_count_journal" )
    # count_payment = fields.Integer(string="Payments Count",  required=False,compute="_compute_count_payment" )
    state = fields.Selection(string="",tracking=True, selection=[('draft', 'Draft'), ('confirm', 'Confirm'),('paid', 'Paid'),('close', 'Close'),('cancel', 'Canceled'), ],default="draft", required=False, )
    is_close = fields.Boolean(string="",compute="_check_state"  )
    payment_date = fields.Date(readonly=True,tracking=True,copy=False)
    close_date = fields.Date(readonly=True,tracking=True,copy=False)

    @api.constrains('payment_date','close_date')
    def check_pay_and_close_dates(self):
        if self.payment_date and self.close_date:
            if self.close_date < self.payment_date:
                raise exceptions.ValidationError(_('The close date can not be before the payment date!'))

    def action_close_advances(self,ids):
        print("ids == >>> ",ids)
        total=0.0
        for rec in ids:
            if rec.state != 'paid':
                raise exceptions.ValidationError("Can not Close Advance salary [%s] because it's state un paid !" %(rec.name))
            total += rec.remaining
            if rec.on_salary:
                raise exceptions.ValidationError("Can not Close Advance salary With Deduct From Salary !")
        context = dict(self._context) or {}
        context['default_advance_ids'] = [(6, 0, ids.ids)]
        context['default_remaining'] = total
        # print('context == >>> ',context)
        # print('total == >>> ',total)
        # {'default_dst_path': dst_path}
        action = self.env.ref('hr_advance.actiom_close_advances_wizard').read()[0]
        return {
            'name':'Close Advance',
            'type':'ir.actions.act_window',
            'res_model':'close.advances',
            'view_mode':'form',
            'view_type':'form',
            'view_id':self.env.ref('hr_advance.close_advances_form_id').id,
            'context' : context,
            'target':'new',
        }


    @api.constrains('due_date')
    def _check_date(self):
        if self.due_date:
            date_order = datetime.strptime(str(self.due_date), '%Y-%m-%d')
            date_today = datetime.strptime(str(fields.Date.context_today(self)), '%Y-%m-%d')
            if (date_order < date_today):
                raise exceptions.ValidationError(_('The Due date is in the past.'))

    def _compute_count_journal(self):
        for rec in self:
            moves=[]
            if rec.name:
                move_name = 'Loan# ' + rec.name
                moves_obj = self.env['account.move'].search([('ref', '=', move_name)])
                if moves_obj:
                    moves =moves_obj.ids
            self.count_journal = len(moves)
    # def _compute_count_payment(self):
    #     for rec in self:
    #         moves = []
    #         moves_obj = self.env['account.payment'].search([('ref', '=', rec.name)])
    #         if moves_obj:
    #             moves = moves_obj.ids
    #         self.count_payment = len(moves)
    def action_cancel(self):
        self.state='cancel'
    @api.depends('paid_amount','amount')
    def _compute_remaining(self):

        self.remaining=self.amount - self.paid_amount

        pass

    # def action_open_payment(self):
    #     for rec in self:
    #         payment = self.env['account.payment'].search([('ref', '=', rec.name)])
    #         domain = [('id', 'in', payment.ids)]
    #         view_tree = {
    #             'name': _(' Payments '),
    #             'view_type': 'form',
    #             'view_mode': 'tree,form',
    #             'res_model': 'account.payment',
    #             'type': 'ir.actions.act_window',
    #             'domain': domain,
    #             'readonly': True,
    #         }
    #         return view_tree

    def action_open_order(self):
        for rec in self:
            move_name = 'Loan# ' + rec.name
            account_move = self.env['account.move'].search([('ref', '=',move_name)])
            domain = [('id', 'in', account_move.ids)]
            view_tree = {
                'name': _(' Journal Entries '),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'domain': domain,
                'readonly': True,
            }
            return view_tree
    @api.depends('num_install','amount')
    def _compute_install_value(self):
        inst_value=0.0
        if self.on_salary and self.num_install>0:
            inst_value= self.amount/self.num_install
        self.install_value=inst_value


    def create_install(self):
        today = fields.Date.today()
        if self.due_date:
            today=self.due_date

        print('today == ', today)
        date1 = datetime.strptime(str(today), "%Y-%m-%d")
        date2 = date1.strftime("%Y-%m")
        day = int(date1.strftime("%d"))
        contract_date = datetime.strptime(date2, "%Y-%m")
        print('contract_date == ', contract_date)
        lst = []
        x = 0
        if self.install_value and self.num_install > 0:
            for i in range(self.num_install):
                print("i == ", i)
                print("x == ", x)

                xx = contract_date + relativedelta(months=+x) + relativedelta(days=(day - 1))
                d = xx.date()
                print('xx= ', xx)
                print('d= ', d)
                rec = self.env['pay.advance.line'].create({'amount': self.install_value,
                                                           'advance_id': self.id,
                                                           'due_date': d
                                                           })
                lst.append(rec.id)
                x += 1
            self.write({'installment_ids': [(6, 0, lst)]})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('adv.sel') or 'New'
        new_record= super(advance_salary, self).create(vals)
        if new_record.on_salary and new_record.num_install>0  :
            new_record.create_install()
        return new_record
    def write(self, values):
        rec = super(advance_salary, self).write(values)
        if 'num_install' in values or 'amount' in values or 'due_date' in values:
            self.create_install()
        return rec

    def unlink(self):
        if any(rec.state != 'draft' for rec in self):
            raise exceptions.ValidationError(_('Cannot delete a Advance Salary After Confirm'))
        return super(advance_salary, self).unlink()


    def copy_data(self, default=None):
        if default is None:
            default = {}
        default['remaining'] = self.amount
        default['paid_amount'] = 0.0
        return super(advance_salary, self).copy_data(default)

    @api.depends('installment_ids')
    def _check_state(self):
        if self.state != 'close':
            index=0
            for line in self.installment_ids:
                if line.is_post:
                    index += 1
            if index == len(self.installment_ids) !=0:
                self.write({'state':'close'})
                self.is_close=True
            else:
                self.is_close=False
        else:
            self.is_close = False

    def action_confirm(self):
        self.state = 'confirm'


    def confirm(self):
        partner=self.env['res.partner']
        debit_account = []
        credit_account = []
        currency_id = self.company_id.currency_id
        if self.employee_id.address_home_id:
            partner=self.employee_id.address_home_id

        elif self.employee_id.user_id:
            partner = self.employee_id.user_id.partner_id
        else:
            raise exceptions.ValidationError("the employee Don't have partner")
        move = {
            'journal_id': self.journal_id.id,
            'ref': self.name,
            'company_id': self.company_id.id,
            'date': self.payment_date,
        }
        move_line = {
            'name': '/',
            'partner_id': partner.id,
            'ref': self.name,
            'date': self.payment_date,
        }
        if self.advance_type.debit_account_id:
            debit_account.append({'account': self.journal_id.default_debit_account_id.id, 'percentage': 100})
            credit_account.append({'account': partner.property_account_payable_id.id, 'percentage': 100})

        for debit in debit_account:
            if not debit['account']:
                raise exceptions.ValidationError("Debit Account Can't Be Null")
        for credit in credit_account:
            if not credit['account']:
                raise exceptions.ValidationError("Credit Account Can't Be Null")


        move = self.create_move_lines(move=move, move_line=move_line,
                                      debit_account=debit_account,
                                      credit_account=credit_account,
                                      src_currency=currency_id,
                                      amount=self.amount)



    def create_move_lines(self, **kwargs):
        journals = []
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        company_currency = self.env['res.users'].search([('id', '=', self._uid)]).company_id.currency_id

        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=datetime.today()).compute_amount_fields(kwargs['amount'], kwargs['src_currency'],
                                                         company_currency, False)
        move_vals = {
            'journal_id': kwargs['move']['journal_id'],
            'date': kwargs['move'].get('date') or fields.Date.today(),
            'ref': kwargs['move']['ref'],
            'company_id': kwargs['move']['company_id']
        }

        move = self.env['account.move'].with_context({}).create(move_vals)
        self.show_move_id = move.id

        for index in kwargs['debit_account']:
            debit_line_vals = {
                'name': kwargs['move_line']['name'],
                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'ref': kwargs['move_line']['ref'],
                'debit': (index['percentage'] / 100) * kwargs['amount'],
                'credit': credit,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
            }
            debit_line_vals['move_id'] = move.id
            aml_obj.create(debit_line_vals)
            # move.line_ids.with_context({}).create(debit_line_vals)
        # move.post()

        for index in kwargs['credit_account']:
            credit_line_vals = {
                'name': kwargs['move_line']['name'],
                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'ref': kwargs['move_line']['ref'],
                'debit': credit,
                'credit': (index['percentage'] / 100) * kwargs['amount'],
                'amount_currency': -1 * amount_currency,
            }
            credit_line_vals['move_id'] = move.id
            # move.line_ids.with_context({}).create(credit_line_vals)
            aml_obj.create(credit_line_vals)
        move.post()
        return move

class pay_advance_line(models.Model):
    _name = 'pay.advance.line'


    amount = fields.Float(string="Amount",  required=False, )
    due_date = fields.Date(string="Due date", required=False, )
    advance_id = fields.Many2one(comodel_name="advance.salary", string="Advance", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False,related='advance_id.employee_id' , store=True)
    is_post = fields.Boolean(string="post",  )
