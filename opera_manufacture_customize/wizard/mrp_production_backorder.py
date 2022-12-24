""" Initialize  Init """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class MrpProductionBackorder(models.TransientModel):
    """
        Inherit Mrp Production Backorder:
         -
    """
    _inherit = 'mrp.production.backorder'

    def action_backorder(self):
        ctx = dict(self.env.context)
        ctx.pop('default_mrp_production_ids', None)
        mo_ids_to_backorder = self.mrp_production_backorder_line_ids.filtered(lambda l: l.to_backorder).mrp_production_id.ids
        return self.mrp_production_ids.with_context(ctx, skip_backorder=True, mo_ids_to_backorder=mo_ids_to_backorder).button_mark_done()


class MrpWorkorderAdditionalProduct(models.TransientModel):
    """
        Initialize Mrp Workorder Additional Product:
         -
    """
    _inherit = 'mrp_workorder.additional.product'
    _description = 'Mrp Workorder Additional Product'

    def add_product(self):
        """ Override add_product """
        return super(MrpWorkorderAdditionalProduct, self.sudo()).add_product()