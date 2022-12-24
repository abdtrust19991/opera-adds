""" Initialize Res User """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class ResUsers(models.Model):
    """
        Inherit Res Users:
         - 
    """
    _inherit = 'res.users'
    
    stock_location_route_ids = fields.Many2many(
        'stock.location.route'
    )