# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _ ,tools, SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
import pytz
from datetime import datetime , date ,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from odoo.fields import Datetime as fieldsDatetime
import calendar
from odoo import http
from odoo.http import request
from odoo import tools
import xlwt
from xlwt import Formula
import base64
from io import BytesIO

import logging

LOGGER = logging.getLogger(__name__)

class ProductCardReportWizard(models.TransientModel):
    _name = 'product.card.report.wizard'

    name = fields.Char()
    default_code = fields.Char()
    product_id = fields.Many2one(comodel_name="product.product")
    product_tmpl_id = fields.Many2one(comodel_name="product.template")
    date_from = fields.Datetime(default=lambda self: fields.Datetime.now(), required=False, )
    date_to = fields.Datetime(default=lambda self: fields.Datetime.now(), required=False, )
    location_id = fields.Many2one(comodel_name="stock.location",)
    report_type = fields.Selection(string="Status",default="xls", selection=[('xls', 'XLS'), ('html', 'HTML'), ], required=True, )
    excel_sheet_name = fields.Char(string="", required=False, )
    excel_sheet = fields.Binary(string="",  )

    @api.model
    def default_get(self, fields_list):
        res = super(ProductCardReportWizard,self).default_get(fields_list)
        if self.env.context.get('active_model') == 'product.template':
            product = self.env['product.template'].browse(self.env.context.get('active_id'))
            res['product_tmpl_id'] = self.env.context.get('active_id')
            res['name'] = product.name
            res['default_code'] = product.default_code
        elif self.env.context.get('active_model') == 'product.product':
            product = self.env['product.product'].browse(self.env.context.get('active_id'))
            res['name'] = product.display_name
            res['product_id'] = product.id
            res['default_code'] = product.default_code
        return res

    def convert_date_to_utc(self,dat, tz):
        local = tz and pytz.timezone(tz) or pytz.timezone('UTC')
        date = local.localize(dat, is_dst=None)
        date = date.astimezone(pytz.utc)
        date.strftime('%Y-%m-%d %H:%M:%S')
        return date.replace(tzinfo=None)

    def convert_date_to_local(self,dat, tz):
        local = tz and pytz.timezone(tz) or pytz.timezone('UTC')
        dat = dat.replace(tzinfo=pytz.utc)
        dat = dat.astimezone(local)
        dat.strftime('%Y-%m-%d: %H:%M:%S')
        return dat.replace(tzinfo=None)

    def get_data_from_move(self,move,qty,inc,out,qty_balance):
        picking = move.picking_id
        order_ref = ''
        picking_origin = ''
        url_ref = ''
        url_order_ref = ''
        if picking:
            picking_origin = picking.origin
            url_ref = '/web#id=%s&model=stock.picking&view_type=form' % (picking.id)
            types = ['sale_id', 'purchase_id']
            for ot in types:
                if picking[ot]:
                    order_ref = picking[ot].name
                    url_order_ref = '/web#id=%s&model=%s&view_type=form' % (picking[ot].id, picking[ot]._name)
            if not order_ref and 'pos.order' in self.env:
                pos_order = self.env['pos.order'].search([('picking_ids', 'in', picking.ids)])
                order_ref = pos_order.name
                if not pos_order:
                    pos_order = self.env['pos.order'].search([('name', '=', picking_origin)])
                    order_ref = pos_order.name
                if pos_order:
                    url_order_ref = '/web#id=%s&model=%s&view_type=form' % (pos_order.id, pos_order._name)

        return {
            'date': str(self.convert_date_to_local(fields.Datetime.from_string(move.date), self.env.user.tz)),
            'ref': move.reference,
            'order_ref': order_ref or '',
            'picking_origin': picking_origin,
            'url_ref': url_ref,
            'url_order_ref': url_order_ref,
            'partner': move.partner_id.name or move.picking_id.partner_id.name or '',
            'from': move.location_id.complete_name,
            'to': move.location_dest_id.complete_name,
            'qty_in': qty if inc else 0,
            'qty_out': qty if out else 0,
            'qty_balance': qty_balance,
        }


    def get_report_data(self):
        data=[]
        # product = self.product_id
        products = self.product_id if self.product_id else self.product_tmpl_id.product_variant_ids
        date_to_utc = fields.Datetime.from_string(self.date_to) if self.date_to else datetime.now()
        date_from_utc = fields.Datetime.from_string(self.date_from) if self.date_from else None
        domain = [('product_id', 'in', products.ids), ('state', '=', 'done')]
            
        company_id = self.env.user.company_id.id
        qty_balance = 0
        if self.location_id:
            internal_locations = self.location_id
        else:
            internal_locations = self.env['stock.location'].search([('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])])

        if self.date_from:
            date_from_utc = fields.Datetime.from_string(self.date_from)
            domain.append(('date','>=',str(date_from_utc)))
            if self.product_tmpl_id:
                qty_balance = self.product_tmpl_id.with_context(to_date=date_from_utc,location=self.location_id.id).qty_available
            else:
                qty_balance = self.product_id.with_context(to_date=date_from_utc,location=self.location_id.id).qty_available
                

            data.append({
                'date': str(self.convert_date_to_local(fields.Datetime.from_string(self.date_from),self.env.user.tz)),
                'ref': '',
                'order_ref': '',
                'partner': '',
                'from': '',
                'to': '',
                'qty_in': '',
                'qty_out': '',
                'qty_balance': qty_balance,
            })

        if self.date_to:
            domain.append(('date','<=',str(date_to_utc)))

        if self.location_id:
            domain.extend(['|',('location_id', 'child_of', self.location_id.id),('location_dest_id', 'child_of', self.location_id.id)])

        stock_move = self.env['stock.move'].search(domain,order='date asc,id asc')
        for move in stock_move:

            inc = True if move.location_dest_id in internal_locations else False
            out = True if move.location_id in internal_locations else False
            qty = move.quantity_done

            previous_qty_balance = data[-1]['qty_balance'] if data else 0

            if out and not inc :
                sign = -1
            elif not out and inc:
                sign = 1
            else:
                sign = 0

            qty_balance = previous_qty_balance + sign * qty

            line_data = self.get_data_from_move(move,qty,inc,out,qty_balance)
            data.append(line_data)

        if stock_move and not date_from_utc:
            date_from_utc = fields.Datetime.from_string(stock_move[0].date)

        return data,date_to_utc,date_from_utc

    def add_excel_sheet(self,workbook,data,date_to_utc,date_from_utc,sheet_name):
        worksheet = workbook.add_sheet(sheet_name)

        lang = self.env.user.lang
        if lang == "ar_SY":
            worksheet.cols_right_to_left = 1

        # worksheet.col(0).width = 256 * 10
        # worksheet.col(1).width = 256 * 50
        # worksheet.col(2).width = 256 * 30
        TABLE_HEADER = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour tan, pattern_back_colour tan'
        )

        TABLE_HEADER_batch = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour light_green, pattern_back_colour light_green'
        )
        header_format = xlwt.easyxf(
            'font: bold 1, name Aharoni , color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'alignment: wrap 1;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour gray25, pattern_back_colour gray25'
        )
        TABLE_HEADER_payslib = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour silver_ega, pattern_back_colour silver_ega'
        )
        TABLE_HEADER_Data = TABLE_HEADER
        TABLE_HEADER_Data.num_format_str = '#,##0.00_);(#,##0.00)'
        STYLE_LINE = xlwt.easyxf(
            'align: vertical center, horizontal center, wrap off;',
            'borders: left thin, right thin, top thin, bottom thin; '
            # 'num_format_str: General'
        )
        STYLE_Description_LINE = xlwt.easyxf(
            'align: vertical center, horizontal left, wrap 1;',
            'borders: left thin, right thin, top thin, bottom thin;'
        )

        TABLE_data = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index black,height 150;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour white, pattern_back_colour white'
        )
        TABLE_data.num_format_str = '#,##0.00'
        xlwt.add_palette_colour("gray11", 0x11)
        workbook.set_colour_RGB(0x11, 222, 222, 222)
        TABLE_data_tolal_line = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index white,height 200;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour blue_gray, pattern_back_colour blue_gray'
        )

        # TABLE_data_tolal_line.num_format_str = '#,##0.00'
        TABLE_data_o = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index black,height 150;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour gray11, pattern_back_colour gray11'
        )
        STYLE_LINE_Data = STYLE_LINE
        STYLE_LINE_Data.num_format_str = '#,##0.00_);(#,##0.00)'

        worksheet.panes_frozen = True
        worksheet.set_horz_split_pos(5)
        row = 0
        worksheet.write_merge(row, row, 0, 1, _('اسم الصنف'), TABLE_data)
        worksheet.write_merge(row, row , 2, 6,self.name, TABLE_data)
        worksheet.write_merge(row, row , 7, 8, _('كود الصنف'), TABLE_data)
        worksheet.write(row, 9, self.product_id.default_code, TABLE_data)

        row = 1
        worksheet.write_merge(row, row, 0, 1, _('التاريخ من'), TABLE_data)
        worksheet.write_merge(row, row , 2, 3,str(self.convert_date_to_local(date_from_utc,self.env.user.tz)) if date_from_utc else '', TABLE_data)
        worksheet.write_merge(row, row , 4, 5, _('التاريخ الى'), TABLE_data)
        worksheet.write_merge(row, row , 6, 7, str(self.convert_date_to_local(date_to_utc,self.env.user.tz)), TABLE_data)
        if self.location_id:
            worksheet.write_merge(row, row , 8, 9, _('مخزن'), TABLE_data)
            worksheet.write_merge(row, row , 10, 11,self.location_id.complete_name, TABLE_data)

        row = 3
        col = 0
        worksheet.row(row).height = 256 * 5
        worksheet.row(row+1).height = 256 * 5
        worksheet.write_merge(row, row + 1, col, col, _('تاريخ'), header_format)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, _('رقم الأذن'), header_format)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, _('مرجع الأذن'), header_format)
        col += 1
        # worksheet.write_merge(row, row + 1, col, col, _('مرجع المخزن'), header_format)
        # col += 1
        worksheet.write_merge(row, row + 1, col, col, _('اسم المورد/العميل'), header_format)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, _('من مخزن'), header_format)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, _('الى مخزن'), header_format)
        col += 1
        worksheet.write(row, col , _('وارد'), header_format)
        col += 1
        worksheet.write(row, col, _('منصرف'), header_format)
        col += 1
        worksheet.write(row, col, _('رصيد'), header_format)
        col = 6
        worksheet.write(row+1,col, _('كمية'), header_format)
        col += 1
        worksheet.write(row+1,col, _('كمية'), header_format)
        col += 1
        worksheet.write(row+1,col, _('كمية'), header_format)
        col += 1
        worksheet.col(0).width = 256 * 50
        row += 1
        for d in data:
            row += 1
            col = 0
            worksheet.write(row, col, d['date'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['ref'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['order_ref'], TABLE_data)
            # col += 1
            # worksheet.write(row, col, d['picking_origin'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['partner'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['from'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['to'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['qty_in'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['qty_out'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['qty_balance'], TABLE_data)
            col += 1


    def action_print_xls(self):
        self.ensure_one()
        workbook = xlwt.Workbook()
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError(_('The start date can not be after end date'))

        if self.date_to and not self.date_from:
            raise ValidationError(_('Start date is not set'))

        report_data,date_to_utc,date_from_utc = self.get_report_data()
        self.add_excel_sheet(workbook, report_data,date_to_utc,date_from_utc, _('كارت صنف قيمة'))


        xls_file_path = (_( self.name + ' كارت صنف قيمة.xls'))

        output = BytesIO()

        workbook.save(output)
        self.excel_sheet = base64.b64encode(output.getvalue())
        self.excel_sheet_name = xls_file_path
        output.close()
        return {
            'type': 'ir.actions.act_url',
            'name': 'Stock Card',
            'url': '/web/download_xls/%s/%s' % (self._name, self.id),
            'target': 'new'
        }

    def action_print_html(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/custom/product_card/%s' %(self.id),
            'target': 'current'
        }

    def action_print(self):
        if self.report_type == 'xls':
            return self.action_print_xls()

        elif self.report_type == 'html':
            return self.action_print_html()


