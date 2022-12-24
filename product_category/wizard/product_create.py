# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class CreateProductWizard(models.TransientModel):
    _name = 'create.product.wizard'

    purchase_id = fields.Many2one(comodel_name="purchase.order", string="PO", required=False, readonly=True)

    year = fields.Many2one(comodel_name="year.code", string="Year", size=2, required=True, )
    manufacture = fields.Many2one(comodel_name="manufacture.code", string="Country", size=1, required=True, )
    season = fields.Many2one(comodel_name="season.code", string="Season", size=1, required=True, )
    activity_id = fields.Many2one(comodel_name="activity.code", required=True)
    color_id = fields.Many2one(comodel_name="product.template.attribute.value",
                               domain="[('display_type', '=', 'color')]", required=True)
    size_id = fields.Many2one(comodel_name="product.template.attribute.value",
                              domain="[('display_type', '=', 'size')]", required=True)
    item = fields.Char('Item Number')
    year_activity = fields.Char('year activity')
    categ_id = fields.Many2one(comodel_name="product.category", string="Category", required=True, )
    barcode = fields.Char(string="Internal Reference", compute="compute_barcode", store=True, )
    prod_name = fields.Char(string="Product Name", required=True, )
    attribute_line_ids = fields.One2many(comodel_name='product.attribute.line.wizard', inverse_name="wizard_id",
                                         string='Product Attributes', )

    @api.onchange('year', 'activity_id')
    def onchange_year_activity(self):
        code = ''
        if self.year:
            code += str(self.year.code)
        if self.activity_id:
            code += str(self.activity_id.code)
        self.year_activity = code

    @api.constrains('year', 'season', 'manufacture')
    def _check_fields(self):
        self.onchange_year()

    @api.onchange('year', 'manufacture', 'season')
    def onchange_year(self):
        if self.year:
            if len(str(self.year.code)) > 2:
                raise ValidationError(_('You can not enter more than 2 digit in field year!'))
        if self.manufacture:
            if len(str(self.manufacture.code)) > 2:
                raise ValidationError(_('You can not enter more than 1 digit in field Country!'))
        if self.season:
            if len(str(self.season.code)) > 2:
                raise ValidationError(_('You can not enter more than 1 digit in field Season!'))
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

    @api.depends('year', 'manufacture', 'season', 'categ_id', 'size_id', 'color_id', 'item', 'activity_id')
    def compute_barcode(self):
        code = ''
        if self.year:
            code += str(self.year.code)
        if self.activity_id:
            code += str(self.activity_id.code)
        if self.item:
            code += self.item
        if self.manufacture:
            code += str("-" + self.manufacture.code)
        if self.season:
            code += str(self.season.code)
        if self.color_id:
            code += str(self.color_id.code)
        if self.size_id:
            code += str(self.size_id.code)
        self.barcode = code

    @api.onchange('year_activity')
    def onchange_item_number(self):
        year = ''
        activity = ''
        if self.year:
            year += str(self.year.code)
        if self.activity_id:
            activity += str(self.activity_id.code)
        if self.year and self.activity_id:
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

    # @api.depends('year', 'manufacture', 'season', 'categ_id', )
    # def compute_barcode(self):
    #     code = ''
    #     if self.year:
    #         code += str(self.year.code)
    #     if self.manufacture:
    #         code += str(self.manufacture.code)
    #     if self.season:
    #         code += str(self.season.code)
    #     if self.season and self.manufacture and self.year:
    #         seq = "001"
    #         products = self.env['product.product'].search([('default_code', 'like', code)])
    #         products = products and products.filtered(lambda prod: prod.base_code == code).sorted('default_code',
    #                                                                                               reverse=True)
    #         if products:
    #             seq = int(products[0].default_code[-3:])
    #             seq = str(seq + 1)
    #             if len(seq) < 3:
    #                 seq = seq.zfill(3)
    #         code += str(seq)
    #     self.barcode = code

    @api.onchange('attribute_line_ids')
    def onchange_attribute_line_ids(self):
        size_id = self.env.ref('product_category.add_product_attribute_size').id
        for rec in self.attribute_line_ids:
            print("rec == ", rec)
            if rec.attribute_id.id == size_id:
                for v in rec.value_ids:
                    if not v.code:
                        raise ValidationError(
                            _('You Must enter code  for size :  %s !.') % v.name)
                continue
            # else:
            #     if len(rec.value_ids)>1:
            #         raise ValidationError(_('You can not enter more than 1 Value For attribute %s.')
            #         % rec.attribute_id.name)

    def create_product(self):
        if self.categ_id and self.prod_name:
            vals = {
                'name': self.prod_name,
                'default_code': self.barcode,
                'type': 'product',
                'season_id': self.season.id,
                'country_id': self.manufacture.id,
                'year_id': self.year.id,
                'available_in_pos': True,
                'categ_id': self.categ_id.id,
            }
            vals['attribute_line_ids'] = []

            for att in self.attribute_line_ids:
                vals['attribute_line_ids'].append(
                    (0, 0, {'attribute_id': att.attribute_id.id, 'value_ids': [], })
                )
                for att_val in att.value_ids:
                    vals['attribute_line_ids'][-1][2]['value_ids'].append((4, att_val.id))
            product_tmpl = self.env['product.template'].sudo().create(vals)

            # print("hhhhhh product_variant_ids ",product_tmpl.product_variant_ids)

            variants = product_tmpl.product_variant_ids
            variants_nu = len(product_tmpl.product_variant_ids)
            if variants_nu > 1:
                for vrnt in variants:
                    vrnt.default_code = str(self.barcode)
                    vrnt.barcode = vrnt.default_code + str(
                        vrnt.product_template_attribute_value_ids[0].product_attribute_value_id.code)

            lines = []
            for rec in product_tmpl.product_variant_ids:
                lines.append((0, 0, {
                    'product_id': rec.id,
                    'name': rec.name,
                    'price_unit': rec.lst_price,
                    'product_uom': rec.uom_id.id,
                    'product_qty': 1,
                    'order_id': self.purchase_id.id,
                    'date_planned': self.purchase_id.date_order,
                }))
            # print("lines ==> ",lines)
            self.purchase_id.order_line = lines


class ProductAttributeLineWizard(models.TransientModel):
    _name = 'product.attribute.line.wizard'
    _description = 'Product Attribute Line Wizard'

    wizard_id = fields.Many2one(comodel_name="create.product.wizard", string="", required=False, )
    attribute_id = fields.Many2one(comodel_name="product.attribute", string="", required=False, )
    value_ids = fields.Many2many(comodel_name="product.attribute.value", domain="[('attribute_id','=',attribute_id)]")
