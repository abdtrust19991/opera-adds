""" Initialize Purchase Order """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class PurchaseOrder(models.Model):
    """
        Inherit Purchase Order:
         -
    """
    _inherit = 'purchase.order'

    production_id = fields.Many2one(
        'mrp.production',
        compute='_compute_production_id'
    )

    @api.depends('order_line.move_dest_ids.group_id.mrp_production_ids')
    def _compute_production_id(self):
        """ Compute production_id value """
        for rec in self:
            mrp_production_ids = (rec.order_line.move_dest_ids.group_id.mrp_production_ids | rec.order_line.move_ids.move_dest_ids.group_id.mrp_production_ids)
            if mrp_production_ids:
                rec.production_id = mrp_production_ids[0].id
            else:
                rec.production_id = None
