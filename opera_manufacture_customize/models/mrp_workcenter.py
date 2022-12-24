""" Initialize Mrp Workcenter """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class MrpWorkcenter(models.Model):
    """
        Inherit Mrp Workcenter:
         -
    """
    _inherit = 'mrp.workcenter'

    workcenter_overhead_cost_line_ids = fields.One2many(
        'workcenter.overhead.cost.line',
        'workcenter_id'
    )