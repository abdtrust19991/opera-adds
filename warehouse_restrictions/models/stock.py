# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning



class picking(models.Model):
    _inherit = 'stock.picking'

    allowed_users = fields.Many2many(related='picking_type_id.allowed_users')

    @api.onchange('location_id')
    def onchange_user(self):
        res = {}
        user = self.env.user
        user_locations = user.location_ids.ids
        if user_locations and self.picking_type_id.code == 'internal':

            # self.location_dest_id = user_locations[0]
            res.update({
                'domain': {
                    'location_dest_id': [('id', 'in', user_locations)],

                }
            })
            return res

    @api.constrains('state', 'location_id', 'location_dest_id')
    def check_user_location_rights(self):
        # self.ensure_one(
        for rec in self:
            if rec.state == 'draft' or rec.picking_type_id.code != 'internal':
                print("11 picking_type_id",rec.picking_type_id.code)
                return True
            user_locations = rec.env.user.location_ids
            if rec.env.user.restrict_locations and rec.picking_type_id.code == 'internal':
                print("22 not empty")
                message = _(
                    'Invalid Location. You cannot process this move since you do '
                    'not control the location "%s". '
                    'Please contact your Adminstrator.')
                if rec.location_id not in user_locations:
                    if rec.location_id != rec.env.user.default_location_id:
                        raise Warning(message % rec.location_id.display_name)
                elif rec.location_dest_id not in user_locations:
                    raise Warning(message % rec.location_dest_id.display_name)


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.constrains('state', 'location_id', 'location_dest_id')
    def check_user_location_rights(self):
        for rec in self:
            if rec.state == 'draft' or rec.picking_type_id.code == 'internal':
                return True
            user_locations = rec.env.user.stock_location_ids
            if rec.env.user.restrict_locations and rec.picking_type_id.code != 'internal':
                message = _(
                    'Invalid Location. You cannot process this move since you do '
                    'not control the location "%s". '
                    'Please contact your Adminstrator.')
                if rec.location_id not in user_locations:
                    raise Warning(message % rec.location_id.name)
                elif rec.location_dest_id not in user_locations:
                    raise Warning(message % rec.location_dest_id.name)

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    use_rfq = fields.Boolean(string="Use In RFQ", )
    allowed_users = fields.Many2many(comodel_name="res.users", relation="stock_picking_type_users_rel", column1="user_id", column2="picking_type_id")

    def _get_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        pickings = self.env['stock.picking'].search([('picking_type_id','=',self.id)])
        action['domain'] = [('id','in',pickings.ids)]
        if self:
            action['display_name'] = self.display_name
        return action


class StockLocation(models.Model):
    _inherit = 'stock.location'

    user_ids = fields.Many2many(
        'res.users',
        'location_security_stock_location_users',
        'location_id',
        'user_id',
        'Allowed Users')

