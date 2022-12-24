# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductSticker(models.Model):
    _name = 'product.sticker'
    _description = 'Product sticker used on product image'

    POSITIONS = [('top-left','Top Left'),('top-right','Top Right'),('bottom-left','Bottom Left'),
                ('bottom-right','Bottom Right')]

    name = fields.Char(string='Name', translate=True, required=True)
    sticker_text = fields.Char(string='Sticker Text', translate=True)
    bg_color = fields.Char(string='Background Color',
                help='Here you can specify the HTML color for the background of product label')
    text_color = fields.Char(string='Text Color',
                help='Here you can specify the HTML color for the font color of product label')
    font_size = fields.Integer(string='Font Size', help='For ex. 10')
    top = fields.Integer(string='Top Margin(px)', help='For ex. 10')
    bottom = fields.Integer(string='Bottom Margin(px)', help='For ex. 10')
    left = fields.Integer(string='Left Margin(px)', help='For ex. 10')
    right = fields.Integer(string='Right Margin(px)', help='For ex. 10')
    height = fields.Integer(string='Height(px)', help='For ex. 100')
    width = fields.Integer(string='Width(px)', help='For ex. 100')
    rotate = fields.Integer(string='Rotate', help='For ex. -25, 45')
    image = fields.Binary(string='Image')
    cut_corner = fields.Boolean(string='Cut the corner')
    sticker_type = fields.Selection([('image','Image'),('html','HTML')], default='image', required=True)
    shape = fields.Selection([('square','Square'),('circle','Circle'),('rectangle','Rectangle')], default='circle')
    position = fields.Selection(POSITIONS, string='Position', required=True, default='top-left')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_sticker_ids = fields.Many2many('product.sticker', string='product stickers')
    product_rating = fields.Float(string='Product Rating', compute='_compute_product_rating', store=True)
    product_banner = fields.Binary(string='Product Banner')
    product_tags_ids = fields.Many2many('product.tags', string='Product Tags')

    @api.depends('message_ids')
    def _compute_product_rating(self):
        for i in self:
            prodRating = round(i.sudo().rating_get_stats().get('avg') / 1 * 100) / 100
            i.product_rating = prodRating
