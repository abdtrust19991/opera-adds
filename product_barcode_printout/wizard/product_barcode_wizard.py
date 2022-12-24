# -*- coding: utf-8 -*-
""" init object """
import base64
from odoo import fields, models, api, _ ,tools, SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from datetime import datetime , date ,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from odoo.fields import Datetime as fieldsDatetime
import calendar
from odoo import http
from odoo.http import request
from odoo import tools

import logging

LOGGER = logging.getLogger(__name__)


class PoBarcodeWizard(models.TransientModel):
    _name = 'product.barcode.wizard'
    _description = 'product.barcode.wizard'

    state = fields.Selection(string="Status",default="draft", selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ], required=False, )
    quantity_to_print = fields.Integer(default=1, required=True, )
    line_ids = fields.One2many(comodel_name="product.barcode.line.wizard", inverse_name="wizard_id", string="", required=False, )

    def get_barcode_files_wizard(self, report):
        data = {'product_qty': self.quantity_to_print}
        pdf = self.env.ref(report)._render_qweb_pdf(self._context.get('active_id'), data=data)[0]
        pdf = base64.b64encode(pdf)
        file_name = 'Product Labels'
        self.state = 'confirmed'
        wiz_line = self.env['product.barcode.line.wizard'].create(
            {'wizard_id': self.id,
             'binary_field':pdf,
             'file_name':file_name}
        )

        view_form = {
            'name': _('Product Barcode '),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.barcode.wizard',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',

        }

        return view_form

    def print_large_label(self):
        view_form = self.get_barcode_files_wizard('product_barcode_printout.report_product_many_label')
        return view_form


class PoBarcodeWizardLine(models.TransientModel):
    _name = 'product.barcode.line.wizard'
    _description = 'product.barcode.line.wizard'

    file_name = fields.Char()
    binary_field = fields.Binary(string="File")
    wizard_id = fields.Many2one(comodel_name="product.barcode.wizard" )
