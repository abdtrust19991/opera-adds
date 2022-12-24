""" Initialize Model """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class StockPicking(models.Model):
    """
        Inherit Stock Picking:
         - 
    """
    _inherit = 'stock.picking'

    # is_validated_picking = fields.Boolean()

    # def write(self, vals):
    #     """ Override write """
    #     res = super(StockPicking, self).write(vals)
    #     for rec in self:
    #         if rec.state == 'done':
    #             if rec.create_uid != rec.env.user and not rec.env.user.has_group('stock_limitation.super_warehouse_manager'):
    #                 # self._compute_products_availability()
    #                 raise ValidationError('You Must Have Super Warehouse Manager Group To Edit !')
    #         else:
    #             if rec.create_uid != rec.env.user and not rec.env.user.has_group(
    #                     'stock_limitation.super_warehouse_manager'):
    #                 # self._compute_products_availability()
    #                 raise ValidationError('You Must Have Super Warehouse Manager Group To Edit !')
    #     return res

    def button_validate(self):
        # rec =
        for x in self.move_ids_without_package:
            # avail_qty = self.env['stock.quant']._get_available_quantity(x.product_id, x.location_dest_id)
            # print(avail_qty)
            if (x.reserved_availability < x.product_uom_qty):
                raise ValidationError(_("There is not enough quantity to do the transfer (%s > %s)!" % (x.product_uom_qty,x.reserved_availability,)))

        return super(StockPicking, self).button_validate()
