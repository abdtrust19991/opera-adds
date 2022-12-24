# -*- coding: utf-8 -*-

from odoo import fields, models, api

class SliderLayoutOptions(models.Model):
    _name = 'product_var_slider.options'
    _description = 'Product Variant Slider Layout Options'

    name = fields.Char(string='Name', translate=True, required=True)
    theme_id = fields.Many2one('ir.module.module', ondelete='cascade', string='Theme', required=True)

class ProductVariantCollection(models.Model):
    _name = 'slider_var.collection.configure'
    _description = 'Product Variant Collections'

    name = fields.Char(string='Title', translate=True, required=True)
    active = fields.Boolean(string='Active', default=True)
    website_id = fields.Many2one('website', string='Website')
    product_variant_ids = fields.One2many('slider_var.products', 'collec_id', string='Products', required=True)

    @api.depends('website_id')
    def _current_theme(self):
        self.theme_id = self.website_id.theme_id.id

class ProductVarianrSlider(models.Model):
    _name = 'slider_var.products'
    _order = 'sequence,id'
    _description = 'Products Variant Collection for Slider'

    product_id = fields.Many2one('product.product', string='Products', domain=[('website_published', '=', True)])
    sequence = fields.Integer(string='Sequence')
    collec_id = fields.Many2one('slider_var.collection.configure', string='Collection')
