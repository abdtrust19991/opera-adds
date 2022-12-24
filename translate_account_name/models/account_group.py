""" Initialize Account """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class AccountGroup(models.Model):
    """
        Inherit Account Group:
         -
    """
    _inherit = 'account.group'

    name = fields.Char(
        translate=True
    )
