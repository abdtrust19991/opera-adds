# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.tools.translate import html_translate

class Faq(models.Model):
    _name = "faq"
    _inherit = ['website.published.multi.mixin']
    _description = "FAQ"
    _rec_name = "question"

    question = fields.Char(string="Question", translate=True, required=True)
    answer = fields.Html(string="Answer", required=True, translate=html_translate)
