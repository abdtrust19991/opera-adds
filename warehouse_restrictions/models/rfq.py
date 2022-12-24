# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning



class purchase(models.Model):
    _inherit = 'purchase.order'


    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    create_uid = fields.Many2one(comodel_name="res.users", string="Responsible", required=False,default=lambda self: self._uid)

    @api.onchange('create_uid')
    def onchange_create_uid(self):
        res = {}
        user = self.env.user
        print("user == ",user)
        if user.default_picking_type_ids:
            lst_ids = self.env['stock.picking.type'].search([('id', 'in', user.default_picking_type_ids.ids),('use_rfq', '=',True)]).ids
            if lst_ids:
                self.picking_type_id=lst_ids[0]
                print("lst_ids == ", lst_ids)
            res.update({
                'domain': {
                    'picking_type_id': [('id', '=', list(set(lst_ids)))],

                }
            })
            print("res == ",res)
            if not lst_ids:
                self.picking_type_id = False
            return res
       
# class stock_picking_type(models.Model):
#     _inherit = 'stock.picking.type'
#
#     use_rfq = fields.Boolean(string="Use In RFQ",  )
