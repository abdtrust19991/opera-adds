# -*- coding: utf-8 -*-

import io
import json
import base64
from PIL import Image

from odoo.exceptions import ValidationError
from odoo.tools.mimetypes import guess_mimetype
from odoo import api, exceptions, fields, models, _


class Website(models.Model):
    _inherit = "website"

    is_pwa_active = fields.Boolean(string='PWA', help="Enable PWA.")
    pwa_name = fields.Char(string='Name')
    pwa_short_name = fields.Char(string='Short Name')
    pwa_theme_color = fields.Char(string='Theme Color')
    pwa_description = fields.Char(string='Description')
    pwa_bg_color = fields.Char(string='Background Color')
    pwa_big_image = fields.Binary(string='Icon')
    pwa_small_image = fields.Binary(compute='_compute_small_image', store=True)

    @api.depends('pwa_big_image')
    def _compute_small_image(self):
        for r in self:
            if(r.pwa_big_image):
                decoded_pwa_image = base64.b64decode(r.pwa_big_image)
                icon_bytes = io.BytesIO(decoded_pwa_image)
                getimg = Image.open(icon_bytes)
                resizeImageSmall = getimg.resize((192,192))
                img_byt_arr_sm = io.BytesIO()
                resizeImageSmall.save(img_byt_arr_sm, format='PNG')
                img_byt_arr_sm = img_byt_arr_sm.getvalue()
                getNewSmImage = base64.b64encode(img_byt_arr_sm)
                r.pwa_small_image = getNewSmImage

    @api.constrains('pwa_big_image')
    def _constrains_image(self):
        for i in self:
            if(i.pwa_big_image):
                decoded_pwa_image = base64.b64decode(i.pwa_big_image)
                pwa_image_mimetype = guess_mimetype(decoded_pwa_image)
                if not pwa_image_mimetype.startswith('image/png'):
                    raise exceptions.UserError(_('You can only upload PNG format image!'))
                icon_bytes = io.BytesIO(decoded_pwa_image)
                image_size = Image.open(icon_bytes).size
                if(image_size[0] < 512 and image_size[1] < 512):
                    raise exceptions.UserError(_('Image pixel should not less then 512x512!'))
                elif(image_size[0] != image_size[1]):
                    raise exceptions.UserError(_('Icon must be of square shape!'))
                elif(image_size[0] > 512 and image_size[1] > 512):
                    getimg = Image.open(icon_bytes)
                    resizeImg = getimg.resize((512,512))
                    img_byt_arr = io.BytesIO()
                    resizeImg.save(img_byt_arr, format='PNG')
                    img_byt_arr = img_byt_arr.getvalue()
                    getNewImage = base64.b64encode(img_byt_arr)
                    i.pwa_big_image = getNewImage


class PwaConfigs(models.TransientModel):
    _inherit = "res.config.settings"

    is_pwa_active = fields.Boolean(string='PWA', related='website_id.is_pwa_active', readonly=False, help="Enable PWA")
    pwa_name = fields.Char(string='Name', related='website_id.pwa_name', readonly=False)
    pwa_short_name = fields.Char(string='Short Name', related='website_id.pwa_short_name', readonly=False)
    pwa_theme_color = fields.Char(string='Theme Color', related='website_id.pwa_theme_color', readonly=False)
    pwa_description = fields.Char(string='Description',  related='website_id.pwa_description', readonly=False)
    pwa_bg_color = fields.Char(string='Background Color', related='website_id.pwa_bg_color', readonly=False)
    pwa_big_image = fields.Binary(string='Icon', related='website_id.pwa_big_image', readonly=False)
    pwa_small_image = fields.Binary(related='website_id.pwa_small_image', readonly=False)