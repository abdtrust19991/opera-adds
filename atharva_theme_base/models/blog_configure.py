# -*- encoding: utf-8 -*-

from odoo import fields, models

class BlogConfigure(models.Model):
    _name = 'blog.configure'
    _description = 'Blog Configuration for Blog Snippets'

    name = fields.Char(string='Blog Slider Title', translate=True)
    blog_ids = fields.Many2many('blog.post', string='Blog Post', domain=[('website_published','=',True)])
    active = fields.Boolean(string='Active', default=True)
