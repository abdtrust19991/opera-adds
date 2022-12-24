from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, Warning


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        # import pdb;pdb.set_trace()
        if 'year_id' in values or 'country_id' in values or 'season_id' in values or 'size_id' in values or 'color_id' in values or 'item' in values or 'activity_id' in values:
            for product in self.product_variant_ids:
                product.compute_barcode()
                product.compute_default_code()

    @api.model
    def create(self, values):
        res = super(ProductTemplate, self).create(values)
        # import pdb;pdb.set_trace()
        if 'year_id' in values or 'country_id' in values or 'season_id' in values or 'size_id' in values or 'color_id' in values or 'item' in values or 'activity_id' in values:
            for product in res.product_variant_ids:
                product.compute_barcode()
                product.compute_default_code()
        return res

    @api.depends('barcode')
    def compute_default_code(self):
        if self.barcode:
            self.default_code = self.barcode

    @api.depends('year_id', 'country_id', 'season_id', 'categ_id', 'size_id', 'color_id', 'item', 'activity_id')
    def compute_barcode(self):
        for rec in self:
            code = ''
            if rec.year_id:
                code += str(rec.year_id.code)
            if rec.activity_id:
                code += str(rec.activity_id.code)
            if rec.item:
                code += rec.item
            if rec.country_id:
                code += str("-" + rec.country_id.code)
            if rec.season_id:
                code += str(rec.season_id.code)
            if rec.color_id:
                code += str(rec.color_id.code)
            if rec.size_id:
                code += str(rec.size_id.code)
            rec.barcode = code


class Product(models.Model):
    _inherit = 'product.product'

    base_code = fields.Char(
        compute='_compute_base_code'
    )
    barcode = fields.Char(
        'Barcode',
    )
    default_code = fields.Char(
        'Internal Reference',
    )
    color_id = fields.Many2one(
        comodel_name="product.template.attribute.value",
        compute="compute_color_variant",
        domain="[('display_type', '=', 'color')]"
    )
    size_id = fields.Many2one(
        comodel_name="product.template.attribute.value",
        compute="compute_size_variant",
        domain="[('display_type', '=', 'size')]"
    )

    def compute_color_variant(self):
        for res in self:
            if res.product_template_attribute_value_ids:
                res.color_id = res.product_template_attribute_value_ids.filtered(lambda i: i.display_type == "color")
            else:
                res.color_id = res.product_tmpl_id.color_id.id

    def compute_size_variant(self):
        for res in self:
            if res.product_template_attribute_value_ids:
                res.size_id = res.product_template_attribute_value_ids.filtered(lambda i: i.display_type == "size")
            else:
                res.size_id = res.product_tmpl_id.size_id.id

    @api.onchange('year_id', 'country_id', 'season_id', 'size_id', 'color_id', 'item', 'activity_id')
    def compute_barcode(self):
        for rec in self:
            code = ''
            if rec.year_id:
                code += str(rec.year_id.code)
            if rec.activity_id:
                code += str(rec.activity_id.code)
            if rec.item:
                code += rec.item
            if rec.country_id:
                code += str("-" + rec.country_id.code)
            if rec.season_id:
                code += str(rec.season_id.code)
            if rec.color_id:
                code += str(rec.color_id.code)
                print(rec.color_id.name)
                print(rec.color_id.code)
            if rec.size_id:
                code += str(rec.size_id.code)
                print(rec.size_id.name)
                print(rec.size_id.code)
            print(code)
            print(rec)
            rec.barcode = code

    @api.onchange('barcode')
    def compute_default_code(self):
        for rec in self:
            if rec.barcode:
                rec.default_code = rec.barcode
            else:
                rec.default_code = ""
