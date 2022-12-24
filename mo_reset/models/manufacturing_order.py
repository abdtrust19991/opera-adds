from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools import float_is_zero, float_compare


class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    set_to_draft = fields.Boolean('Set to Draft')

    @api.depends(
        'move_raw_ids.state', 'move_raw_ids.quantity_done', 'move_finished_ids.state',
        'workorder_ids.state', 'product_qty', 'qty_producing')
    def _compute_state(self):
        for production in self:
            if not production.state or production.set_to_draft is True:
                production.state = 'draft'
            elif production.state == 'cancel' or (
                    production.move_raw_ids and all(move.state == 'cancel' for move in production.move_raw_ids)):
                production.state = 'cancel'
            elif production.state == 'done' or (production.move_raw_ids and all(
                    move.state in ('cancel', 'done') for move in production.move_raw_ids)):
                production.state = 'done'
            # elif production.workorder_ids and all(wo_state in ('done', 'cancel') for wo_state in
            #                                       production.workorder_ids.mapped(
            #                                               'state')) and not production.set_to_draft:
            elif production.workorder_ids and all(wo_state == 'done' for wo_state in
                                                  production.workorder_ids.mapped(
                                                          'state')) and not production.set_to_draft:
                for wo_state in production.workorder_ids.mapped('state'):
                    print('Wo State ', wo_state)
                print('Wo production.set_to_draft ', production.set_to_draft)
                production.state = 'to_close'
            elif not production.workorder_ids and production.qty_producing >= production.product_qty and not production.set_to_draft:
                production.state = 'to_close'
            elif any(wo_state in ('progress', 'done') for wo_state in production.workorder_ids.mapped('state')):
                production.state = 'progress'
            elif production.product_uom_id and not float_is_zero(production.qty_producing,
                                                                 precision_rounding=production.product_uom_id.rounding):
                production.state = 'progress'
            elif any(not float_is_zero(move.quantity_done,
                                       precision_rounding=move.product_uom.rounding or move.product_id.uom_id.rounding)
                     for move in production.move_raw_ids):
                production.state = 'progress'

    def action_draft(self):
        self.move_raw_ids.write({'state': 'draft'})
        # self.move_raw_ids = False
        # self.move_finished_ids = False
        self.write({'set_to_draft': True})
        self.write({'state': 'draft'})
        print(self.state)
        return True

    def action_confirm(self):
        self.write({'set_to_draft': False})
        res = super(ManufacturingOrder, self).action_confirm()
        return res

    def button_plan(self):
        self.write({'set_to_draft': False})
        res = super(ManufacturingOrder, self).button_plan()
        return res

    def button_unplan(self):
        self.write({'set_to_draft': False})
        res = super(ManufacturingOrder, self).button_unplan()
        return res

    def action_cancel(self):
        self.write({'set_to_draft': False})
        res = super(ManufacturingOrder, self).action_cancel()
        return res
