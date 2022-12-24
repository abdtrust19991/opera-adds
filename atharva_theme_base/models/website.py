# -*- coding: utf-8 -*-

from odoo import fields, models

class CustomWebsite(models.Model):
    _inherit = 'website'

    def get_website_faq_list(self):
        faqs = self.env['faq'].sudo().search([('website_id', 'in', (False, self.get_current_website().id)),
        ('is_published', '=', True)])
        return faqs