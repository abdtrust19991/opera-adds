""" Initialize Stock Backorder """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class StockBackorderConfirmation(models.TransientModel):
    """
        Inherit Stock Backorder Confirmation:
         -
    """
    _inherit = 'stock.backorder.confirmation'


    def process_cancel_backorder(self):
        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            return self.env['stock.picking'] \
                .browse(pickings_to_validate) \
                .with_context(skip_backorder=True, picking_ids_not_to_backorder=self.pick_ids.ids) \
                .button_validate()
        return True
