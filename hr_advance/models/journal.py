# -*- coding: utf-8 -*-

from odoo import api, fields, models, _,exceptions
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta


class NewModule(models.Model):
    _inherit = 'account.journal'

    adv_pay_close = fields.Boolean(string="Use in Payment and Close Advance Salary",  )

class account_payment(models.Model):
    _inherit = 'account.payment'

    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=False,
                                        oldname="payment_method")

