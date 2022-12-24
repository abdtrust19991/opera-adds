# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import html_translate

class MixedLinks(models.Model):
    _name = 'megamenu.links'
    _description = 'Website Megamenu Mixed Links'

    link_type = fields.Selection(selection=[('product.public.category', 'Category'),
                        ('website.page', 'Page'),('product.template', 'Product')],
                        string='Link Type', default='product.public.category')
    name = fields.Char(string='Name', translate=True)
    link_category = fields.Many2one('product.public.category', string='Category Name',
                            domain=['|', ('parent_id', '=', False), ('parent_id.parent_id', '=', False)])
    link_pages = fields.Many2one('website.page', string='Page Name',
                        domain=[('website_published', '=', True)])
    link_products = fields.Many2one('product.template', string='Product Name',
                        domain=[('website_published', '=', True)])
    url = fields.Char(string='URL', default='#')
    description = fields.Char(string='Description')
    pos_row = fields.Integer(string='Row-Position')
    pos_column = fields.Integer(string='Column-Position')
    image = fields.Binary(string='Image', store=True)
    image_name = fields.Char(string='Image Name')
    megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')

    @api.onchange('link_type')
    def setRelationSelection(self):
        self.update({'link_category': None, 'link_pages': None,
                     'link_products': None, 'url': None, 'name': None})

    @api.onchange('link_category', 'link_pages', 'link_products')
    def setNameUrl(self):
        """ set name URL in website megamenu options """
        if self.link_type == 'product.public.category':
            if self.link_category:
                self.update({'name': self.link_category.name,
                             'url': '/shop/category/' + str(self.link_category.id)})
            else:
                self.update({'name': None, 'url': None})
        elif self.link_type == 'website.page':
            if self.link_pages:
                self.update({'name': self.link_pages.name,
                             'url': self.link_pages.url})
            else:
                self.update({'name': None, 'url': None})
        elif self.link_type == 'product.template':
            if self.link_products:
                self.update({'name': self.link_products.name,
                             'url': '/shop/product/' + str(self.link_products.id)})
            else:
                self.update({'name': None, 'url': None})
        else:
            self.update({'name': None, 'url': None})

class ContentSectionGroup(models.Model):
    _name = 'megamenu.content_section'
    _description = 'Website Megamenu HTML Content Section'

    name = fields.Char(string='Name', translate=True)
    content_section_pos = fields.Integer(string='Content Section Position')
    content_html = fields.Html(string='Content HTML', translate=html_translate)
    megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')

class ColumnHeadline(models.Model):
    _name = 'megamenu.column_headline'
    _description = 'Website Megamenu Column Heading'

    name = fields.Char(string='Title', translate=True, required=True)
    headline_link = fields.Char(string='Headline Link')
    description = fields.Text(string='Description')
    pos_column = fields.Integer(string='Column-Position')
    megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')

class CategoryThirdLevel(models.Model):
    _name = 'megamenu.categories_menu_lines'
    _order = 'sequence desc,id'
    _description = 'Website Megamenu 3-Levels Category Links'

    name = fields.Char(string='Title', translate=True, required=True)
    categ_id = fields.Many2one(
        'product.public.category', string='Category Name', required=True)
    level = fields.Integer(string='Level')
    sequence = fields.Integer(string='Sequence', default=10)
    image = fields.Binary(string='Image', store=True)
    image_name = fields.Char(string='Image Name')
    megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')

class MegamenuContent(models.Model):
    _name = 'megamenu.content'
    _description = 'Website Megamenu Content'

    has_label = fields.Boolean()
    label_text = fields.Char()
    label_bg_color = fields.Char(string='Label bgcolor')
    label_text_color = fields.Char(string='Label text color')

    name = fields.Char(string='Content Name', translate=True)
    active = fields.Boolean(string='Active', default=True)
    is_header = fields.Boolean(string='Header')
    is_footer = fields.Boolean(string='Footer')
    main_content_type = fields.Selection([('product_grid', 'Product Grid'), ('product_list', 'Product Listing'),
                                          ('category_grid', 'Category Grid'),
                                          ('category_list', 'Category Listing'),
                                          ('content', 'Content'),
                                          ('mixed_list','Mixed Listing'),
                                          ('horiz_categ_toggle','Horizontal Category Toggle'),
                                          ('hamburger_categ_toggle','Hamburger Category Menu')
                                        ], string='Content Type')
    no_of_columns = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')],
                                    string='Number of Columns')
    product_ids = fields.Many2many('product.template', string='Products', domain=[
                                   ('website_published', '=', True)])
    product_lable_color = fields.Char(string='Product Label Color')
    header_content = fields.Html(string='Header Content', translate=html_translate)
    footer_content = fields.Html(string='Footer Content', translate=html_translate)
    category_ids = fields.Many2many('product.public.category', string='Category',
                                    domain=['|', ('parent_id', '=', False), ('parent_id.parent_id', '=', False)])
    category_lable_color = fields.Char(string='Category Label Color')
    menu_content = fields.Html(string='Content', translate=html_translate)
    background_image = fields.Binary(string='Background Image')
    background_image_pos = fields.Selection(selection=[('left', 'Left'), ('right', 'Right')],
                                            string='Background Image Position',
                                            default='left')
    link_ids = fields.One2many(
        'megamenu.links', 'megamenu_id', string='Linked Item')
    content_section_ids = fields.One2many(
        'megamenu.content_section', 'megamenu_id', string='Content Sections')
    column_headline_ids = fields.One2many(
        'megamenu.column_headline', 'megamenu_id', string='Column Headlines')
    category_first_level = fields.One2many(
        'megamenu.categories_menu_lines', 'megamenu_id', string='First Level Categories', domain=[('level', '=', 1)])
    category_second_level = fields.One2many(
        'megamenu.categories_menu_lines', 'megamenu_id', string='Second Level Categories', domain=[('level', '=', 2)])
    category_third_level = fields.One2many(
        'megamenu.categories_menu_lines', 'megamenu_id', string='Third Level Categories', domain=[('level', '=', 3)])

    slider_image_option = fields.Selection([('slider', 'Slider'), ('image', 'Image')],
                                           string='Show Image/Slider', default='image')
    slider_image_position = fields.Integer(string='Column-Position')

    image_img = fields.Binary(string='Image', store=True)
    image_name = fields.Char(string='Image Name')
    image_title = fields.Char(string='Title')
    image_link = fields.Char(string='Link')
    image_desc = fields.Char(string='Short Description')
    megamenu_slider = fields.One2many(
        'megamenu_slider', 'megamenu_id', string='Slider Lines')
    slider_speed = fields.Char(string='Slider Speed')
    slider_header = fields.Char(string='Name')

class Megamenu_slider(models.Model):
    _name = 'megamenu_slider'
    _description = 'Megamenu Slider'

    slider_image_img = fields.Binary(string='Image', store=True)
    slider_image_name = fields.Char(string='Image Name')
    slider_image_title = fields.Char(string='Title')
    slider_image_link = fields.Char(string='Link')
    slider_image_desc = fields.Char(string='Short Description')
    megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')

class website_menu(models.Model):
    _inherit = 'website.menu'

    is_dynamic_mega_menu = fields.Boolean(string='Dynamic Mega Menu')
    content_id = fields.Many2one('megamenu.content', string='Content')
    parent_id = fields.Many2one('website.menu', 'Parent Menu', index=True,
                                ondelete='cascade', domain=[('is_dynamic_mega_menu', '=', False)])
