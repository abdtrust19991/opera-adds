""" Initialize Product Template """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class ProductTemplate(models.Model):
    """
        Inherit Product Template:
         - 
    """
    _inherit = 'product.template'
    
    can_be_moh = fields.Boolean()