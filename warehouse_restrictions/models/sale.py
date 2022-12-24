# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning



class sale(models.Model):
    _inherit = 'sale.order'




    create_uid = fields.Many2one(comodel_name="res.users", string="Responsible",readonly=True, required=False,default=lambda self: self._uid)

    # picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=READONLY_STATES, required=True,
    #                                    help="This will  operation type of incoming shipment")

    @api.onchange('create_uid')
    def onchange_user(self):
        res = {}
        user = self.env.user
        print("user == ",user)
        if user.default_location_id:
            stock = self.env['stock.warehouse'].search([('lot_stock_id', '=', user.default_location_id.id)])
            if stock:
                self.warehouse_id = stock[0]
            res.update({
                'domain': {
                    'warehouse_id': [('lot_stock_id', '=',user.default_location_id.id)],

                }
            })
            print("res == ",res)
            return res
       

