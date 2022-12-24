# -*- coding: utf-8 -*-

from odoo import fields, models, api

class CommonSliderLayoutOptions(models.Model):
    _name = 'product_slider_common.options'
    _description = 'Product Common Slider Layout Options'

    name = fields.Char(string='Name', translate=True, required=True)
    theme_id = fields.Many2one('ir.module.module', ondelete='cascade', string='Theme', required=True)

class SliderLayoutOptions(models.Model):
    _name = 'product_slider.options'
    _description = 'Product Slider Layout Options'

    name = fields.Char(string='Name', translate=True, required=True)
    theme_id = fields.Many2one('ir.module.module', ondelete='cascade', string='Theme', required=True)

class ProductCollection(models.Model):
    _name = 'slider_temp.collection.configure'
    _description = 'Product Template Collections'

    name = fields.Char(string='Title', translate=True, required=True)
    active = fields.Boolean(string='Active', default=True)
    website_id = fields.Many2one('website', string='Website')
    product_id = fields.One2many('slider_temp.products', 'collec_id', string='Products', required=True)

    @api.depends('website_id')
    def _current_theme(self):
        self.theme_id = self.website_id.theme_id.id

class ProductSlider(models.Model):
    _name = 'slider_temp.products'
    _order = 'sequence,id'
    _description = 'Products Template Collection for Slider'

    website_id = fields.Many2one('website', string='Website')
    product_id = fields.Many2one('product.template', string='Products', domain=[('website_published', '=', True)])
    sequence = fields.Integer(string='Sequence')
    collec_id = fields.Many2one('slider_temp.collection.configure', string='Collection')
