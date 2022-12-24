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
    product_id = fields.Many2one(comodel_name="product.template")
    date_from = fields.Datetime(default=lambda self: fields.Datetime.now(), required=False, )
    date_to = fields.Datetime(default=lambda self: fields.Datetime.now(), required=False, )
    location_id = fields.Many2one(comodel_name="stock.location",)
    report_type = fields.Selection(string="Status",default="xls", selection=[('xls', 'XLS'), ('html', 'HTML'), ], required=True, )
    # warehouse = fields.Many2one(comodel_name="stock.warehouse")

    @api.model
    def default_get(self, fields_list):
        res = super(ProductCardReportWizard,self).default_get(fields_list)
        if self.env.context.get('product.template'):
            product = self.env['product.template'].browse(self.env.context.get('active_id'))
            res['product_id'] = self.env.context.get('active_id')
            res['name'] = product.name
        elif self.env.context.get('product.product'):
            product = self.env['product.product'].browse(self.env.context.get('active_id'))
            product = product.display_name
            res['product_id'] = product.product_tmpl_id.id
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

    def get_amount_from_entries(self,line):
        stock_valuation_account_id = line.product_id.categ_id.property_stock_valuation_account_id.id
        account_moves = line.move_id.account_move_ids
        total_amount = 0
        total_qty = 0
        if account_moves:
            for move in account_moves:
                for line in move.line_ids.filtered(lambda l:l.account_id.id == stock_valuation_account_id):
                    total_amount += line.debit - line.credit
                    total_qty += line.quantity

        return abs(total_amount),total_qty

    def add_cost_adjust(self,price_hist,qty_balance):
        return {
            'date': str(self.convert_date_to_local(fields.Datetime.from_string(price_hist.datetime), self.env.user.tz)),
            'ref': 'Update Price',
            'order_ref': '',
            'picking_origin': '',
            'url_ref': '',
            'url_order_ref': '',
            'partner': '',
            'from': '',
            'to': '',
            'qty_in': '',
            'cost_in': '',
            'amount_in': '',
            'qty_out': '',
            'cost_out': '',
            'amount_out': '',
            'qty_balance': qty_balance,
            'cost_balance': price_hist.cost ,
            'amount_balance': price_hist.cost * qty_balance,
        }


    def get_data_from_line(self,line,qty,cost,amount,inc,out,qty_balance,cost_balance,amount_balance):
        picking = line.picking_id
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
                pos_order = self.env['pos.order'].search([('picking_id', '=', picking.id)])
                order_ref = pos_order.name
                if not pos_order:
                    pos_order = self.env['pos.order'].search([('name', '=', picking_origin)])
                    order_ref = pos_order.name
                if pos_order:
                    url_order_ref = '/web#id=%s&model=%s&view_type=form' % (pos_order.id, pos_order._name)

        return {
            'date': str(self.convert_date_to_local(fields.Datetime.from_string(line.date), self.env.user.tz)),
            'ref': line.reference,
            'order_ref': order_ref or '',
            'picking_origin': picking_origin,
            'url_ref': url_ref,
            'url_order_ref': url_order_ref,
            'partner': line.move_id.partner_id.name or line.move_id.picking_id.partner_id.name or '',
            'from': line.location_id.display_name,
            'to': line.location_dest_id.display_name,
            'qty_in': qty if inc else 0,
            'cost_in': cost if inc else 0,
            'amount_in': amount if inc else 0,
            'qty_out': qty if out else 0,
            'cost_out': cost if out else 0,
            'amount_out': amount if out else 0,
            'qty_balance': qty_balance,
            'cost_balance': cost_balance,
            'amount_balance': amount_balance,
        }

    def get_amount_balance(self,date_from_utc):
        if self.location_id:
            domain = [('product_id','=',self.product_id.id),('state','=','done'),('date', '<', str(date_from_utc)), '|', ('location_id', '=', self.location_id.id),
                      ('location_dest_id', '=', self.location_id.id)]

            stock_move_lines = self.env['stock.move.line'].search(domain)
            balance = 0
            if self.product_id.cost_method == 'fifo':
                for ml in stock_move_lines:
                    # balance += ml.move_id.remaining_value
                    amount, qty = self.get_amount_from_entries(ml)
                    if ml.qty_done and qty:
                        balance += ml.qty_done * amount / qty
                return balance
            else:

                for ml in stock_move_lines:
                    sign = 1 if ml.location_dest_id == self.location_id else -1
                    balance += sign * ml.qty_done * ml.product_id.get_history_price(self.env.user.company_id.id,date=date_from_utc)
                return balance
        else:
            return self.product_id.with_context(to_date=str(date_from_utc)).stock_value

    def get_line_amount(self,line):
        if line.product_id.cost_method != 'fifo':
            amount = line.qty_done * line.product_id.get_history_price(self.env.user.company_id.id, date=line.date)
        else:
            # amount = line.move_id.remaining_value
            amount, qty = self.get_amount_from_entries(line)
            if line.qty_done and qty:
                amount = line.qty_done * amount / qty

        return amount

    def get_report_data(self):
        data=[]
        product = self.product_id
        date_to_utc = fields.Datetime.from_string(self.date_to) if self.date_to else datetime.now()
        date_from_utc = fields.Datetime.from_string(self.date_from) if self.date_from else None
        domain = [('product_id','=',product.id),('state','=','done')]
        company_id = self.env.user.company_id.id
        qty_balance = 0
        if self.location_id:
            internal_locations = self.location_id
        else:
            internal_locations = self.env['stock.location'].search( [('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])])

        if self.date_from:
            date_from_utc = fields.Datetime.from_string(self.date_from)
            domain.append(('date','>=',str(date_from_utc)))
            qty_balance = product.with_context(to_date=date_from_utc,location=self.location_id.id).qty_available
            amount_balance = self.get_amount_balance(date_from_utc)
            cost_balance = amount_balance / qty_balance if qty_balance and self.product_id.cost_method != 'fifo' else 0

            data.append({
                'date': str(self.convert_date_to_local(fields.Datetime.from_string(self.date_from),self.env.user.tz)),
                'ref': '',
                'order_ref': '',
                'partner': '',
                'from': '',
                'to': '',
                'qty_in': '',
                'cost_in': '',
                'amount_in': '',
                'qty_out': '',
                'cost_out': '',
                'amount_out': '',
                'qty_balance': qty_balance,
                'cost_balance':  cost_balance,
                'amount_balance': amount_balance,
            })

        if self.date_to:
            domain.append(('date','<=',str(date_to_utc)))

        if self.location_id:
            domain.extend(['|',('location_id', 'child_of', self.location_id.id),('location_dest_id', 'child_of', self.location_id.id)])
        # if self.warehouse:
        #     domain.append(('move_id.warehouse_id', '=', self.warehouse.id))

        stock_move_lines = self.env['stock.move.line'].search(domain,order='date asc,id asc')
        product_history = self.env['product.price.history'].search([('product_id', '=', self.product_id.id)], order='datetime')
        current_price_hist = product_history[0]
        hist_index = 0
        prev_line = None
        hist_count = len(product_history)
        for line in stock_move_lines:
            while line.date > current_price_hist.datetime and hist_index < hist_count:
                current_price_hist = product_history[hist_index]
                hist_index += 1

            if prev_line and prev_line.date < current_price_hist.datetime < line.date :
                cost_adjust = self.add_cost_adjust(current_price_hist,qty_balance)
                data.append(cost_adjust)
                # hist_index += 1
                # current_price_hist = product_history[hist_index]

            prev_line = line
            inc = True if line.location_dest_id in internal_locations else False
            out = True if line.location_id in internal_locations else False
            qty = line.qty_done

            amount = self.get_line_amount(line)
            # cost = amount/qty if qty and product.cost_method != 'fifo' else 0
            cost = amount/qty if qty else 0
            # qty_balance = product.with_context(to_date=line.date,location=self.location_id.id).qty_available
            previous_amount_balance = data[-1]['amount_balance'] if data else 0
            previous_qty_balance = data[-1]['qty_balance'] if data else 0

            if out and not inc :
                sign = -1
            elif not out and inc:
                sign = 1
            else:
                sign = 0

            qty_balance = previous_qty_balance + sign * qty
            amount_balance = previous_amount_balance + sign * amount
            cost_balance = (amount_balance / qty_balance) if qty_balance and self.product_id.cost_method != 'fifo' else 0

            line_data = self.get_data_from_line(line,qty,cost,amount,inc,out,qty_balance,cost_balance,amount_balance)
            data.append(line_data)

        if stock_move_lines and not date_from_utc:
            date_from_utc = fields.Datetime.from_string(stock_move_lines[0].date)

        balance_columns = 3 if self.product_id.cost_method != 'fifo' else 2
        return data,date_to_utc,date_from_utc,balance_columns

    def add_excel_sheet(self,workbook,data,date_to_utc,date_from_utc,balance_columns,sheet_name):
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
        worksheet.write_merge(row, row , 2, 6,self.product_id.name, TABLE_data)
        worksheet.write_merge(row, row , 7, 8, _('كود الصنف'), TABLE_data)
        worksheet.write(row, 9, self.product_id.default_code, TABLE_data)

        row = 1
        worksheet.write_merge(row, row, 0, 1, _('التاريخ من'), TABLE_data)
        worksheet.write_merge(row, row , 2, 3,str(self.convert_date_to_local(date_from_utc,self.env.user.tz)) if date_from_utc else '', TABLE_data)
        worksheet.write_merge(row, row , 4, 5, _('التاريخ الى'), TABLE_data)
        worksheet.write_merge(row, row , 6, 7, str(self.convert_date_to_local(date_to_utc,self.env.user.tz)), TABLE_data)
        if self.location_id:
            worksheet.write_merge(row, row , 8, 9, _('مخزن'), TABLE_data)
            worksheet.write_merge(row, row , 10, 11,self.location_id.display_name, TABLE_data)

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
        worksheet.write_merge(row, row, col, col+2, _('وارد'), header_format)
        col += 3
        worksheet.write_merge(row, row, col, col+2, _('منصرف'), header_format)
        col += 3
        worksheet.write_merge(row, row, col, col+balance_columns - 1, _('رصيد'), header_format)
        col = 6
        worksheet.write(row+1,col, _('كمية'), header_format)
        col += 1
        worksheet.write(row+1,col, _('سعر'), header_format)
        col += 1
        worksheet.write(row+1,col, _('قيمة'), header_format)
        col += 1
        worksheet.write(row+1,col, _('كمية'), header_format)
        col += 1
        worksheet.write(row+1,col, _('سعر'), header_format)
        col += 1
        worksheet.write(row+1,col, _('قيمة'), header_format)
        col += 1
        worksheet.write(row+1,col, _('كمية'), header_format)
        col += 1
        if balance_columns == 3:
            worksheet.write(row+1,col, _('سعر'), header_format)
            col += 1
        worksheet.write(row+1,col, _('قيمة'), header_format)
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
            worksheet.write(row, col, d['cost_in'] or ' - ', TABLE_data)
            col += 1
            worksheet.write(row, col, d['amount_in'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['qty_out'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['cost_out'] or ' - ', TABLE_data)
            col += 1
            worksheet.write(row, col, d['amount_out'], TABLE_data)
            col += 1
            worksheet.write(row, col, d['qty_balance'], TABLE_data)
            col += 1
            if balance_columns == 3:
                worksheet.write(row, col, d['cost_balance'] or ' - ', TABLE_data)
                col += 1
            worksheet.write(row, col, d['amount_balance'], TABLE_data)

    def action_print_xls(self):
        self.ensure_one()
        workbook = xlwt.Workbook()
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError(_('The start date can not be after end date'))

        if self.date_to and not self.date_from:
            raise ValidationError(_('Start date is not set'))

        report_data,date_to_utc,date_from_utc,balance_columns = self.get_report_data()
        self.add_excel_sheet(workbook, report_data,date_to_utc,date_from_utc,balance_columns, _('كارت صنف قيمة'))


        xls_file_path = (_( self.product_id.name + ' كارت صنف قيمة.xls'))

        output = BytesIO()

        workbook.save(output)

        attachment_model = self.env['ir.attachment']
        attachment_model.search([('res_model', '=', 'product.card.report.wizard'), ('res_id', '=', self.id)]).unlink()
        attachment_obj = attachment_model.create({
            'name': xls_file_path,
            'res_model': 'product.card.report.wizard',
            'res_id': self.id,
            'type': 'binary',
            'db_datas': base64.b64encode(output.getvalue()),
        })

        # Close the String Stream after saving it in the attachments
        output.close()
        url = '/web/content/%s/%s' % (attachment_obj.id,   xls_file_path)
        return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}

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


