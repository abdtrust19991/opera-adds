""" Initialize Workcenter Overhead Cost Line """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class WorkcenterOverheadCostLine(models.Model):
    """
        Initialize Workcenter Overhead Cost Line:
         -
    """
    _name = 'workcenter.overhead.cost.line'
    _description = 'Workcenter Overhead Cost Line'

    product_id = fields.Many2one(
        'product.product',
        domain="[('can_be_moh', '=', True)]",
        required=1
    )
    cost_per_hour = fields.Float(
        string='Cost Per Hour',
        related='product_id.standard_price',
        store=1
    )
    workcenter_id = fields.Many2one(
        'mrp.workcenter'
    )
