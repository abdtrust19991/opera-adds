# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class BrandSliderLayoutOptions(models.Model):
    _name = 'brand_slider.options'
    _description = 'Brand Slider Layout Options'

    name = fields.Char(string='Name',translate=True, required=True)
    theme_id = fields.Many2one('ir.module.module', ondelete='cascade', string='Theme', required=True)

class BrandCollection(models.Model):
    _name = 'slider_brand.collection.configure'
    _description = 'Slider Brand Collection'

    name = fields.Char(string='Group Name', translate=True, required=True)
    active = fields.Boolean(string='Active', default=True)
    website_id = fields.Many2one('website', string='Website')
    theme_id = fields.Many2one('ir.module.module', ondelete='cascade', string='Theme', compute='_current_theme')
    slider_layout_option_id = fields.Many2one('brand_slider.options', string='Slider Layout Option',
                                required=True, help='Select the Slider Layout Options')
    brand_ids = fields.One2many('slider_temp.brands', 'tab_id', string='Brands')
    item_count = fields.Integer(string='Total Count', default=4)
    auto_slider = fields.Boolean(string='Auto Slider', default=True)
    slider_time = fields.Integer(string='Slider Time (Seconds)', default=5)
    label_active = fields.Boolean(string='Show Label', default=True)
    brand_name_active = fields.Boolean(string='Show Brand Name', default=True)
    brand_link_active = fields.Boolean(string='Set Brand link', default=True)

    @api.depends('website_id')
    def _current_theme(self):
        self.theme_id = self.website_id.theme_id.id

    @api.model
    def create(self, vals):
        if not vals.get('brand_ids', ''):
            raise ValidationError(_('Please Add Brands..!!'))
        else:
            return super(BrandCollection, self).create(vals)

class BrandSlider(models.Model):
    _name = 'slider_temp.brands'
    _order = 'sequence,id'
    _description = 'Brand Collection for Slider'

    brand_id = fields.Many2one('as.product.brand', string='Brands')
    sequence = fields.Integer(string='Sequence')
    tab_id = fields.Many2one('slider_brand.collection.configure', string='Tab Id')
