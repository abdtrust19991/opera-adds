# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CatSliderLayoutOptions(models.Model):
    _name = 'cat_slider.options'
    _description = 'Category Slider Layout Options'

    name = fields.Char(string='Name', translate=True, required=True)
    theme_id = fields.Many2one('ir.module.module', ondelete='cascade', string='Theme', required=True)

class CategoryCollection(models.Model):
    _name = 'slider_cat.collection.configure'
    _description = 'Slider Category Collection'

    name = fields.Char(string='Group Name', translate=True, required=True)
    active = fields.Boolean(string='Active', default=True)
    website_id = fields.Many2one('website', string='Website')
    theme_id = fields.Many2one('ir.module.module', ondelete='cascade', string='Theme', compute='_current_theme')
    cat_ids = fields.One2many('slider_temp.cat', 'tab_id', string='Categories')
    slider_layout_option_id = fields.Many2one('cat_slider.options', string='Slider Layout Option',
                                required=True, help='Select the Slider Layout Options')
    @api.depends('website_id')
    def _current_theme(self):
        self.theme_id = self.website_id.theme_id.id

class CategorySlider(models.Model):
    _name = 'slider_temp.cat'
    _order = 'sequence,id'
    _description = 'Category Collection for Slider'

    sequence = fields.Integer(string='Sequence')
    tab_id = fields.Many2one('slider_cat.collection.configure', string='Tab Id')
    cat_id = fields.Many2one('product.public.category', string='Category',
                    domain=[('enable_category_slider', '=', True)])
