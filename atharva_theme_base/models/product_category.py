# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class CustomCategory(models.Model):
    _inherit = 'product.public.category'

    enable_category_slider = fields.Boolean(string='Show In Website Category Slider',
            help='You can set this category in website category slider snippets.')

    @api.constrains('enable_category_slider')
    def validate_category_image(self):
        if not self.image_1920:
            raise ValidationError(
                _('Please set the Category Image before you set this for snippet.'))

    def get_all_parent_category(self):
        website = self.env['website'].get_current_website()
        domain = [('parent_id','=',False)] + website.website_domain()
        category = self.env['product.public.category'].search(domain)
        return category
