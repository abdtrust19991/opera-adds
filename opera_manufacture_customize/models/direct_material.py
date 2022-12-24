""" Initialize Direct Material """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class DirectMaterial(models.Model):
    """
        Initialize Direct Material:
         -
    """
    _name = 'direct.material'
    _description = 'Direct Material'

    product_id = fields.Many2one(
        'product.product'
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit Of Measure'
    )
    planned_qty = fields.Float()
    actual_qty = fields.Float()
    cost_per_unit = fields.Float(
        compute='_compute_cost_per_unit'
    )
    total_planned_cost = fields.Float(
        compute='_compute_total_planned_cost'
    )
    total_actual_cost = fields.Float(
        compute='_compute_total_actual_cost'
    )
    production_id = fields.Many2one(
        'mrp.production'
    )

    @api.depends('product_id', 'uom_id')
    def _compute_cost_per_unit(self):
        """ Compute cost_per_unit value """
        for rec in self:
            if rec.product_id and rec.uom_id :
                if rec.product_id.uom_id == rec.uom_id:
                    rec.cost_per_unit = rec.product_id.standard_price
                else:
                    qty_converted = rec.uom_id._compute_quantity(1, rec.product_id.uom_id)
                    rec.cost_per_unit = rec.product_id.standard_price * qty_converted
            else:
                rec.cost_per_unit = 0

    @api.depends('cost_per_unit', 'planned_qty')
    def _compute_total_planned_cost(self):
        """ Compute  value """
        for rec in self:
            rec.total_planned_cost = rec.cost_per_unit * rec.planned_qty

    @api.depends('cost_per_unit', 'actual_qty')
    def _compute_total_actual_cost(self):
        """ Compute  value """
        for rec in self:
            rec.total_actual_cost = rec.cost_per_unit * rec.actual_qty