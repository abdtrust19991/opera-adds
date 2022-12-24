""" Initialize Stock Picking """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class StockPicking(models.Model):
    """
        Inherit Stock Picking:
         - 
    """
    _inherit = 'stock.picking'
    
    production_id = fields.Many2one(
        'mrp.production',
        compute='_compute_production_id'
    )

    @api.depends('origin')
    def _compute_production_id(self):
        """ Compute production_id value """
        for rec in self:
            if rec.origin:
                mrp = self.env['mrp.production'].search([('name', '=', rec.origin)])
                if mrp:
                    rec.production_id = mrp.id
                else:
                    rec.production_id = None
            else:
                rec.production_id = None
