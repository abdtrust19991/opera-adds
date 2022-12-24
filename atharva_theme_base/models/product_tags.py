# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductTags(models.Model):
    _name = "product.tags"
    _description = "Product Tags"
    _order = "sequence,id"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True, help="The active field allows you to hide the tag without removing it.")
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of rules.")
    product_ids = fields.Many2many('product.template', string='Products')

    _sql_constraints = [('unique_tag_name', 'unique (name)',"Tag already exists!")]