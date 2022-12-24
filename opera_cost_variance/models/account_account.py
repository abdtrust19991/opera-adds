""" Initialize Account Account """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class AccountAccount(models.Model):
    """
        Inherit Account Account:
         - 
    """
    _inherit = 'account.account'
    
    is_actual_account = fields.Boolean()
    is_estimated_account = fields.Boolean()
    is_variance_account = fields.Boolean()

    @api.onchange('is_variance_account')
    def _onchange_is_variance_account(self):
        """ is_variance_account """
        for rec in self:
            if rec.is_variance_account:
                accounts = self.env['account.account'].search([
                    ('is_variance_account', '=', True)
                ])
                if len(accounts) > 0:
                    raise ValidationError('You can not make variance account more than one account !')