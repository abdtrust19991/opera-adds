""" Initialize Cost Variance """

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero


class CostVariance(models.Model):
    """
        Initialize Cost Variance:
         -
    """
    _name = 'cost.variance'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Cost Variance'

    def _get_default_date_start(self):
        company = self.env.company
        return company.compute_fiscalyear_dates(date.today())['date_from'] if company else None

    name = fields.Char(
        required=True,
        translate=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        required=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account'
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        required=0
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
    frequency = fields.Selection([('month', 'Monthly'), ('quarter', 'Quarterly'), ('year', 'Yearly')],
                                 required=True, default='month')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('run', 'Run'),
         ('confirm', 'Confirm'),
         ('posted', 'Posted'),
         ('cancel', 'Cancelled'),
         ],
        default='draft',
        string='Status'
    )
    date_start = fields.Date(string="Start Date", required=True, default=_get_default_date_start)
    date_stop = fields.Date(string="Stop Date", required=True)
    move_ids = fields.One2many('account.move', 'cost_variance_id', string="Generated Moves")
    move_ids_count = fields.Integer(compute="_compute_move_ids_count")
    actual_account_ids = fields.One2many(
        'actual.account',
        'cost_variance_id'
    )
    estimate_account_ids = fields.One2many(
        'estimate.account',
        'cost_variance_id'
    )

    @api.onchange('date_stop')
    @api.constrains('date_stop')
    def _onchange_date_stop(self):
        """ date_stop """
        for rec in self:
            if rec.date_stop:
                if rec.date_stop >= fields.Date.today():
                    raise ValidationError('You must select date before today !')

    def unlink(self):
        """ Override unlink """
        res = super(CostVariance, self).unlink()
        if self.state == 'posted':
            raise ValidationError('You can delete in this state !')
        return res

    @api.depends('move_ids')
    def _compute_move_ids_count(self):
        for record in self:
            record.move_ids_count = len(record.move_ids)

    def run(self):
        """ Run """
        for rec in self:
            actual_accounts = self.env['account.account'].search([
                ('is_actual_account', '=', True)
            ])
            estimated_accounts = self.env['account.account'].search([
                ('is_estimated_account', '=', True)
            ])
            for line in actual_accounts:
                moves = self.env['account.move.line'].search([
                    ('account_id', '=', line.id),
                    ('date', '>=', rec.date_start),
                    ('date', '<=', rec.date_stop),
                    ('parent_state', '=', 'posted'),
                ])
                debit = sum(moves.mapped('debit'))
                credit = sum(moves.mapped('credit'))
                balance = abs(debit - credit)
                if balance > 0:
                    self.env['actual.account'].create({
                        'account_id': line.id,
                        'cost_variance_id': rec.id,
                        'balance': balance,
                    })
            for line in estimated_accounts:
                moves = self.env['account.move.line'].search([
                    ('account_id', '=', line.id),
                    ('date', '>=', rec.date_start),
                    ('date', '<=', rec.date_stop),
                    ('parent_state', '=', 'posted'),
                ])
                debit = sum(moves.mapped('debit'))
                credit = sum(moves.mapped('credit'))
                balance = abs(debit - credit)
                if balance > 0:
                    self.env['estimate.account'].create({
                        'account_id': line.id,
                        'cost_variance_id': rec.id,
                        'balance': balance,
                    })
            rec.write({
                'state': 'run'
            })

    def set_draft(self):
        """ Set Draft """
        for rec in self:
            rec.actual_account_ids.unlink()
            rec.estimate_account_ids.unlink()
            rec.write({
                'state': 'draft'
            })

    def action_cancel(self):
        """ Set Draft """
        for rec in self:
            if rec.move_ids:
                for move in rec.move_ids:
                    move.button_cancel()
            rec.write({
                'state': 'cancel'
            })

    def confirm(self):
        """ Confirm """
        for rec in self:
            moves = self.env['account.move'].search([
                ('cost_variance_id', '!=', False),
                ('date', '>=', rec.date_start),
                ('date', '<=', rec.date_stop),
                ('state', '=', 'posted'),
            ])
            if moves:
                raise ValidationError("there is move in this time!")
            variance_account = self.env['account.account'].search([
                ('is_variance_account', '=', True)
            ], limit=1)
            actual_amount = sum(rec.actual_account_ids.mapped('balance'))
            estimate_amount = sum(rec.estimate_account_ids.mapped('balance'))
            variance_amount = abs(actual_amount - estimate_amount)
            if rec.actual_account_ids and rec.estimate_account_ids and variance_account:
                move_lines = []
                account_move = self.env['account.move'].create({
                    'ref': '%s: %s --> %s' % (rec.name, str(rec.date_start), str(rec.date_stop)),
                    'date': rec.date_stop,
                    'journal_id': rec.journal_id.id,
                    'cost_variance_id': rec.id,
                })
                for line in rec.estimate_account_ids:
                    debit_vals = {
                        'account_id': line.account_id.id,
                        'debit': line.balance,
                        'move_id': account_move.id,
                        'company_id': rec.company_id.id,
                    }
                    move_lines.append((0, 0, debit_vals))
                for line in rec.actual_account_ids:
                    credit_vals = {
                        'account_id': line.account_id.id,
                        'credit': line.balance,
                        'move_id': account_move.id,
                        'company_id': rec.company_id.id,
                        'analytic_account_id': rec.analytic_account_id.id,
                        'analytic_tag_ids': [(6, 0, rec.analytic_tag_ids.ids)],
                    }
                    move_lines.append((0, 0, credit_vals))
                if actual_amount >= estimate_amount:
                    debit_vals = {
                        'account_id': variance_account.id,
                        'debit': variance_amount,
                        'move_id': account_move.id,
                        'company_id': rec.company_id.id,
                        'analytic_account_id': rec.analytic_account_id.id,
                        'analytic_tag_ids': [(6, 0, rec.analytic_tag_ids.ids)],
                    }
                    move_lines.append((0, 0, debit_vals))
                else:
                    credit_vals = {
                        'account_id': variance_account.id,
                        'credit': variance_amount,
                        'move_id': account_move.id,
                        'company_id': rec.company_id.id,
                        'analytic_account_id': rec.analytic_account_id.id,
                        'analytic_tag_ids': [(6, 0, rec.analytic_tag_ids.ids)],
                    }
                    move_lines.append((0, 0, credit_vals))
                account_move.write({'line_ids': move_lines})
                rec.write({
                    'state': 'confirm'
                })
            else:
                raise ValidationError('You Can not create entry . There is missing values !')

    def post(self):
        """ Post """
        for rec in self:
            if rec.move_ids:
                for move in rec.move_ids:
                    move.action_post()
            else:
                raise ValidationError('There is no journal entry to post !')
            rec.write({
                'state': 'posted'
            })

    def action_view_account_moves(self):
        domain = [('id', 'in', self.move_ids.ids)]
        view_tree = {
            'name': _('Journal Entry'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
        return view_tree


class ActualAccount(models.Model):
    """
        Initialize Actual Account:
         -
    """
    _name = 'actual.account'
    _description = 'Actual Account'

    account_id = fields.Many2one(
        'account.account',
        domain="[('is_actual_account', '=', True)]"
    )
    balance = fields.Float()
    cost_variance_id = fields.Many2one(
        'cost.variance'
    )


class EstimatedAccount(models.Model):
    """
        Initialize Estimated Account:
         -
    """
    _name = 'estimate.account'
    _description = 'Estimated Account'

    account_id = fields.Many2one(
        'account.account',
        domain="[('is_estimated_account', '=', True)]"
    )
    balance = fields.Float()
    cost_variance_id = fields.Many2one(
        'cost.variance'
    )

