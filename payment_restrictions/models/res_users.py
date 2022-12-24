# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models,api

import logging

LOGGER = logging.getLogger(__name__)


class Users(models.Model):

    _inherit = 'res.users'
    payment_type_id = fields.Many2many(comodel_name="payment.type",  string="Payment Type", )
    customer_ids = fields.Many2many(comodel_name="res.partner",  relation="customer_user_rel", column1="customer_id", column2="user_customer_id",string="Customers" )
    vendors_ids = fields.Many2many(comodel_name="res.partner", relation="vendor_user_id", column1="vendor_id", column2="user_vendor_id", string="Vendors" )
    journal_ids = fields.Many2many(comodel_name="account.journal",string="Journals", relation="journal_user_id", column1="journal_id", column2="user_journal_id",domain=[('type','in',['bank','cash'])] )
    destination_journal_ids = fields.Many2many('account.journal', string='Transfer To',relation="journal_trans_user_id", column1="journal_trans_id", column2="user_journal_trans_id", domain=[('type', 'in', ('bank', 'cash'))])

    def write(self, values):
        # Add code here
        print("Users ** ", values)
        return super(Users, self).write(values)


class payment_type(models.Model):
    _name = 'payment.type'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
