# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
from odoo.addons import decimal_precision as dp


class product_att(models.Model):
    _inherit = 'product.template.attribute.line'

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', ondelete='cascade', required=False,
                                      index=True)


class product_att_val(models.Model):
    _inherit = 'product.template.attribute.value'
    product_tmpl_id = fields.Many2one(
        'product.template', string='Product Template',
        required=False, ondelete='cascade', index=True)


class att_value(models.Model):
    _inherit = 'product.attribute.value'

    code = fields.Char(string="Code", required=False, size=2)

    @api.constrains('code')
    def _check_code(self):
        if self.code:
            vcl_plat = self.env['product.attribute.value'].sudo().search(
                [('code', '=', self.code), ('id', '!=', self.id)])
            if vcl_plat:
                raise UserError(_("code must be unique"))
            else:
                pass

    # _sql_constraints = [("unique_code", "UNIQUE(code)",
    #                          _('Code must be unique'))]
    #
