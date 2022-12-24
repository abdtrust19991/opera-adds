# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning



class users(models.Model):
    _inherit = 'res.users'

    location_ids = fields.Many2many(
        'stock.location',
        'rel_location_users',
        'user_id',
        'location_id',
        'Internal Transfers Locations')

    restrict_locations = fields.Boolean('Restrict Location')

    stock_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id',
        'location_id',
        'Stock Locations')

    default_location_id = fields.Many2one(comodel_name="stock.location")

    default_picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel',
        column2='user_id', column1='picking_type_id', string='Default Warehouse Operations')
