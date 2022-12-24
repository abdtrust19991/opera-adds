# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, Warning
import logging

LOGGER = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    season_id = fields.Many2one(
        comodel_name="season.code"
    )
    year_id = fields.Many2one(
        comodel_name="year.code"
    )
    country_id = fields.Many2one(
        comodel_name="manufacture.code"
    )
    activity_id = fields.Many2one(
        comodel_name="activity.code"
    )
    color_id = fields.Many2one(
        comodel_name="product.template.attribute.value",
        domain="[('display_type', '=', 'color')]"
    )
    size_id = fields.Many2one(
        comodel_name="product.template.attribute.value",
        domain="[('display_type', '=', 'size')]"
    )
    item = fields.Char(
        'Item Number'
    )
    year_activity = fields.Char(
        'year activity'
    )

    @api.onchange('year_id', 'activity_id')
    def onchange_year_activity(self):
        for rec in self:
            code = ''
            if rec.year_id:
                code += str(rec.year_id.code)
            if rec.activity_id:
                code += str(rec.activity_id.code)
            rec.year_activity = code

    @api.onchange('year_id', 'country_id', 'season_id', 'size_id', 'color_id', 'item', 'activity_id')
    def onchange_year(self):
        if self.year_id:
            if len(str(self.year_id.code)) > 2:
                raise ValidationError(_('You can not enter more than 2 digit in field year!'))
        if self.country_id:
            if len(str(self.country_id.code)) > 2:
                raise ValidationError(_('You can not enter more than 2 digit in field Country!'))
        if self.season_id:
            if len(str(self.season_id.code)) > 2:
                raise ValidationError(_('You can not enter more than 2 digit in field Season!'))
        if self.size_id:
            if len(str(self.size_id.code)) > 2:
                raise ValidationError(_('You can not enter more than 2 digit in field Size!'))
        if self.color_id:
            if len(str(self.color_id.code)) > 2:
                raise ValidationError(_('You can not enter more than 2 digit in field Color!'))
        if self.activity_id:
            if len(str(self.activity_id.code)) > 2:
                raise ValidationError(_('You can not enter more than 2 digit in field Activity!'))
        if self.item:
            if len(str(self.item)) > 3:
                raise ValidationError(_('You can not enter more than 3 digit in field Item!'))

    @api.onchange('year_activity')
    def onchange_item_number(self):
        year = ''
        activity = ''
        if self.year_id:
            year += str(self.year_id.code)
        if self.activity_id:
            activity += str(self.activity_id.code)
        if self.year_id and self.activity_id:
            seq = ""
            products = self.env['product.product'].search_count(
                [('year_activity', '=', self.year_activity)])
            print(products + 1)
            if products or products == 0:
                seq = str(products + 1)
                if len(seq) < 3:
                    seq = seq.zfill(3)
            self.item = seq
        else:
            self.item = False


class Product(models.Model):
    _inherit = 'product.product'

    base_code = fields.Char(
        compute='_compute_base_code'
    )

    # def compute_color_variant(self):
    #     lis = []
    #     if self.product_template_attribute_value_ids:
    #         for z in self.product_template_attribute_value_ids:
    #             var = self.env["product.template.attribute.value"].search(
    #                 [("id", "=", z.id)], limit=1
    #             )
    #             if var:
    #                 see = self.env["product.attribute.value"].search(
    #                     [("name", "=", var.name)], limit=1
    #                 )
    #                 if see.display_type == 'color':
    #                     self.color_id = var.id
    #                     lis.append(var.id)
    #                 if lis:
    #                     self.color_id = lis[0]
    #                 else:
    #                     self.color_id = False
    #     else:
    #         self.color_id = False

    # def compute_size_variant(self):
    #     lis = []
    #     if self.product_template_attribute_value_ids:
    #         for z in self.product_template_attribute_value_ids:
    #             var = self.env["product.template.attribute.value"].search(
    #                 [("id", "=", z.id)], limit=1
    #             )
    #             if var:
    #                 see = self.env["product.attribute.value"].search(
    #                     [("name", "=", var.name)], limit=1
    #                 )
    #                 if see.display_type == 'size':
    #                     self.size_id = var.id
    #                     lis.append(var.id)
    #                 if lis:
    #                     self.size_id = lis[0]
    #                 else:
    #                     self.size_id = False
    #     else:
    #         self.size_id = False

    @api.depends('default_code', )
    def _compute_base_code(self):
        for record in self:
            if record.default_code and len(record.default_code) >= 7:
                record.base_code = record.default_code[:4]


class ProductValueAttribute(models.Model):
    _inherit = 'product.attribute'
    display_type = fields.Selection([
        ('radio', 'Radio'),
        ('select', 'Select'),
        ('size', 'Size'),
        ('color', 'Color')],
        default='radio',
        required=True,
        help="The display type used in the Product Configurator."
    )

    @api.constrains('name')
    def _check_name(self):
        if self.name:
            vcl_plat = self.env['product.attribute'].sudo().search(
                [('name', '=', self.name), ('id', '!=', self.id)])
            if vcl_plat:
                raise UserError(_("name must be unique"))
            else:
                pass

    @api.constrains('display_type')
    def _check_display_type(self):
        if self.display_type:
            vcl_plat = self.env['product.attribute'].sudo().search(
                [('display_type', '=', self.display_type), ('id', '!=', self.id)])
            if vcl_plat:
                raise UserError(_("display type already exist"))
            else:
                pass


class ProductValue(models.Model):
    _inherit = 'product.template.attribute.value'
    code = fields.Char(
        "code",
        required=True,
        related="product_attribute_value_id.code"
    )
    display_type = fields.Selection(
        related='product_attribute_value_id.display_type',
        readonly=True
    )
