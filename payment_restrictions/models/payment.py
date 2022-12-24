# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models,api,_,exceptions

import logging

LOGGER = logging.getLogger(__name__)


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    currant_user = fields.Many2one(comodel_name="res.users", string="Currant User",compute="_compute_currant_user", required=False, )
    user_allowed_journal_ids = fields.Boolean( string="User Have Journals",compute="_compute_currant_user",)
    user_allowed_des_journal_ids = fields.Boolean(string="User Have Des Journals",compute="_compute_currant_user")

    @api.onchange('partner_type')
    def onchange_partner_type(self):
        self.partner_id=False

    @api.depends('partner_type', 'payment_type', 'name')
    def _compute_currant_user(self):
        self.currant_user = self.env.user.id
        if self.env.user.journal_ids:
            self.user_allowed_journal_ids = True
        else:
            self.user_allowed_journal_ids = False
        if self.env.user.destination_journal_ids:
            self.user_allowed_des_journal_ids = True
        else:
            self.user_allowed_des_journal_ids = False


    @api.onchange('user_allowed_des_journal_ids','payment_type','partner_id','amount','partner_type')
    def onchange_user_allowed_des_journal_ids(self):
        res = {}
        destination_journal_ids = self.env.user.destination_journal_ids
        if destination_journal_ids:
            res.update({
                'domain': {
                    'destination_journal_id': [('id', 'in', list(set(destination_journal_ids.ids)))],

                }
            })
        return res

    @api.onchange('user_allowed_journal_ids','payment_type','partner_id','amount','partner_type')
    def onchange_user_allowed_journal_ids(self):
        res = {}
        journal_ids = self.env.user.journal_ids
        if journal_ids:
            res.update({
                'domain': {
                    'journal_id': [('id', 'in', list(set(journal_ids.ids)))],

                }
            })

        return res


    @api.onchange('currant_user','partner_type')
    def onchange_currant_user(self):
        print("*** 3")
        res = {}
        customer_ids = self.env.user.customer_ids
        vendors_ids = self.env.user.vendors_ids
        if self.partner_type == 'customer':
           if  customer_ids:
                res.update({
                    'domain': {
                        'partner_id': [('id', 'in', list(set(customer_ids.ids)))],

                    }
                })
        if self.partner_type == 'supplier':
           if  vendors_ids:
                res.update({
                    'domain': {
                        'partner_id': [('id', 'in', list(set(vendors_ids.ids)))],

                    }
                })

        return res

    def onchange_payment_type(self):
        if self.payment_type:
            user_types = self.env.user.payment_type_id
            flag =False
            if user_types:
                for rec in user_types:
                    if rec.code == self.payment_type:
                        flag=True
            else:flag=True
            if not flag:
                type =dict(self._fields['payment_type'].selection).get(self.payment_type)
                raise exceptions.ValidationError(_("You are Not Allow to process payment type -  %s ") % type)
    def write(self, values):
        rec = super(AccountPayment, self).write(values)
        self.onchange_payment_type()
        return rec
    @api.model
    def create(self, values):
        rec = super(AccountPayment, self).create(values)
        rec.onchange_payment_type()
        return rec
