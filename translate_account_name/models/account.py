""" Initialize Account """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class AccountAccount(models.Model):
    """
        Inherit Account Account:
         -
    """
    _inherit = 'account.account'

    name = fields.Char(
        translate=True
    )

