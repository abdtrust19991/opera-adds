""" Initialize Model """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class ResPartner(models.Model):
    """
        Inherit Res Partner:
         - 
    """
    _inherit = 'res.partner'
    
    _sql_constraints = [
        ('unique_code', 
         'UNIQUE(code)', 
         'Code must be unique'),
    ]
    
    type_of_partner = fields.Selection(
        [('blank', 'Blank'),
         ('customer', 'Customer'),
         ('vendor', 'Vendor')],
        required=1,
        default='blank',
    )

    code = fields.Char(
        readonly=1,
        copy=False
    )

    @api.model
    def create(self, vals_list):
        """
            Override create method
             - sequence name 
        """
        if vals_list.get('code', _('New')) == _('New'):
            if vals_list['type_of_partner'] == 'customer':
                sequence = self.env['ir.sequence'].next_by_code('customer')
                vals_list.update(code=sequence or '/')
            if vals_list['type_of_partner'] == 'vendor':
                sequence = self.env['ir.sequence'].next_by_code('vendor')
                vals_list.update(code=sequence or '/')
        return super(ResPartner, self).create(vals_list)
