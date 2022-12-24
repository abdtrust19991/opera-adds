# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _
import pytz
import xlwt
import odoo.osv.osv
import re
import base64
from io import BytesIO
import datetime
from datetime import date, time
import pytz

from pytz import timezone

class ItemsReportWizard(models.TransientModel):
    _name = 'items.report.wizard'



    product_id = fields.Many2many(comodel_name="product.product", string="Product Variant", required=False, )
    template_id = fields.Many2many(comodel_name="product.template", string="Product", required=False, )
    categ_ids = fields.Many2many("product.category", string="Product Category", required=False, )
    stock_ids = fields.Many2many("stock.warehouse",string="Warehouse")
    season_ids = fields.Many2many("season.code",string="Season")
    year_ids = fields.Many2many("year.code",string="Year")
    country_ids = fields.Many2many("manufacture.code",string="Country")
    lot_ids = fields.Many2many("stock.production.lot",string="Lot")
    excel_sheet = fields.Binary('Download Report')
    excel_sheet_name = fields.Char(string='Name', size=64)

    @api.onchange('template_id')
    def onchange_template_id(self):
        product_obj = self.env['product.product']
        domain = ['|', ('active', '=', True), ('active', '=', False)]
        lots = self.env['stock.production.lot']
        products = product_obj.sudo().search(domain)
        if self.template_id:
            products = self.env['product.product']
            for rec in self.template_id:
                products += rec.product_variant_ids
            lots = self.env['stock.production.lot'].sudo().search([('product_id','in',products.ids)])
        return {'domain': {'product_id': [('id', '=', products.ids)],'lot_ids': [('id', '=', lots.ids)]}}

    def get_report_data(self):
        data = []
        product_obj = self.env['product.product']
        domain = ['|', ('active', '=', True), ('active', '=', False)]
        if self.categ_ids:
            domain += [('categ_id','in',self.categ_ids.ids)]

        if self.season_ids:
            domain += [('season_id', 'in', self.season_ids.ids)]

        if self.year_ids:
            domain += [('year_id', 'in', self.year_ids.ids)]

        if self.country_ids:
            domain += [('country_id', 'in', self.country_ids.ids)]

        products = product_obj.sudo().search(domain)
        if self.product_id:
            products = self.product_id
        if self.template_id:
            products = self.env['product.product']
            for rec in self.template_id:
                products += rec.product_variant_ids
        stock_ids = self.env['stock.warehouse'].search([])
        if self.stock_ids:
            stock_ids = self.stock_ids
        # if self.start_date:
        locations =  self.env['stock.location'].search(
            [('location_id', 'child_of', stock_ids.mapped('view_location_id').ids)])
        print('products ==> ',products)
        print('products ##==> ',len(products))
        if self.lot_ids:
            for lot in self.lot_ids:
                wh_lst=[]
                for po in lot.purchase_order_ids:
                    wh_lst.append(po.picking_type_id.warehouse_id.name)
                wh = ','.join(wh_lst)
                pos_lots = self.env['pos.pack.operation.lot'].sudo().search([
                    ('lot_name', '=', lot.name),
                    ('product_id', 'in', products.ids),
                ])
                total_qty_in = 0.0
                total_qty_out = 0.0
                total_amt_in = 0.0
                total_amt_out = 0.0
                for line in pos_lots:
                    pos_line = line.pos_order_line_id
                    if pos_line.price_subtotal >= 0.0:
                        total_qty_in += pos_line.qty
                        total_amt_in += pos_line.price_subtotal
                    else:
                        total_qty_out += abs(pos_line.qty)
                        total_amt_out += abs(pos_line.price_subtotal)
                move_sales_in = self.env['stock.move.line'].sudo().search([
                    ('move_id.picking_type_id.warehouse_id', 'in', stock_ids.ids),
                    ('product_id', '=', lot.product_id.id),
                    ('lot_id', '=', lot.id),
                    ('move_id.sale_line_id', '!=', False), ('move_id.picking_code', '=', 'outgoing')
                ])
                move_sales_out = self.env['stock.move.line'].sudo().search([
                    ('move_id.picking_type_id.warehouse_id', 'in', stock_ids.ids),
                    ('product_id', '=', lot.product_id.id),
                    ('lot_id', '=', lot.id),
                    ('move_id.sale_line_id', '!=', False), ('move_id.picking_code', '=', 'incoming')
                ])
                move_purchase = self.env['stock.move.line'].sudo().search([
                    ('move_id.picking_type_id.warehouse_id', 'in', stock_ids.ids),
                    ('product_id', '=', lot.product_id.id),
                    ('lot_id', '=', lot.id),
                    ('move_id.purchase_line_id', '!=', False), ('move_id.picking_code', '=', 'incoming')
                ])

                for line in move_sales_in:
                    move = line.move_id
                    price = move.product_uom_qty * move.sale_line_id.price_unit
                    net_price = price - (price * move.sale_line_id.discount / 100.0)
                    total_qty_in += move.product_uom_qty
                    total_amt_in += net_price
                for line in move_sales_out:
                    move = line.move_id
                    price = move.product_uom_qty * move.sale_line_id.price_unit
                    net_price = price - (price * move.sale_line_id.discount / 100.0)
                    total_qty_out += move.product_uom_qty
                    total_amt_out += net_price

                income_qty = 0.0
                income_amt = 0.0
                for line in move_purchase:
                    move = line.move_id
                    income_qty += move.product_uom_qty
                    income_amt += move.purchase_line_id.price_subtotal
                if total_qty_in > 0.0:
                    sales_per = total_qty_out / total_qty_in * 100
                else:
                    sales_per = 0.0

                if income_qty > 0.0:
                    sales_per2 = total_qty_in / income_qty * 100
                else:
                    sales_per2 = 0.0

                data.append(
                    {
                        'pro_code': lot.product_id.barcode,
                        'season_id': lot.product_id.season_id.season,
                        'year_id': lot.product_id.year_id.year,
                        'country_id': lot.product_id.country_id.manufacture,
                        'pro_name': lot.product_id.name,
                        'avalible_qty': lot.product_qty,
                        'income_qty': income_qty,
                        'income_amt': income_amt,
                        'stock': wh,
                        'lot': lot.name,
                        'sales_qty': total_qty_in,
                        'sales_amt': total_amt_in,
                        'refund_qty': total_qty_out,
                        'refund_amt': total_amt_out,
                        'net_qty': total_qty_in - total_qty_out,
                        'net_amt': total_amt_in - total_amt_out,
                        'sales_per': round(sales_per, 2),
                        'sales_per2': round(sales_per2, 2),

                    }
                )
            return data



        if not self.stock_ids:
            for pro in products:

                pos_lines = self.env['pos.order.line'].sudo().search([
                    ('order_id.picking_type_id.default_location_src_id', 'in', locations.ids),
                    ('product_id', '=', pro.id),
                ])
                total_qty_in=0.0
                total_qty_out=0.0
                total_amt_in=0.0
                total_amt_out=0.0
                for line in pos_lines:
                    if line.price_subtotal >= 0.0:
                        total_qty_in += line.qty
                        total_amt_in += line.price_subtotal
                    else:
                        total_qty_out += abs(line.qty)
                        total_amt_out += abs(line.price_subtotal)

                move_sales_in = self.env['stock.move'].sudo().search([
                    ('picking_type_id.warehouse_id', 'in', stock_ids.ids),
                    ('product_id', '=', pro.id),
                    ('sale_line_id','!=',False),('picking_code','=','outgoing')
                ])
                move_sales_out = self.env['stock.move'].sudo().search([
                    ('picking_type_id.warehouse_id', 'in', stock_ids.ids),
                    ('product_id', '=', pro.id),
                    ('sale_line_id','!=',False),('picking_code','=','incoming')
                ])

                move_purchase = self.env['stock.move'].sudo().search([
                    ('picking_type_id.warehouse_id', 'in', stock_ids.ids),
                    ('product_id', '=', pro.id),
                    ('purchase_line_id','!=',False),('picking_code','=','incoming')
                ])


                for move in move_sales_in:
                    price = move.product_uom_qty*move.sale_line_id.price_unit
                    net_price = price - (price * move.sale_line_id.discount/100.0)
                    total_qty_in += move.product_uom_qty
                    total_amt_in += net_price
                for move in move_sales_out:
                    price = move.product_uom_qty*move.sale_line_id.price_unit
                    net_price = price - (price * move.sale_line_id.discount/100.0)
                    total_qty_out += move.product_uom_qty
                    total_amt_out += net_price

                income_qty=0.0
                income_amt=0.0
                for move in move_purchase:
                    income_qty += move.product_uom_qty
                    income_amt += move.purchase_line_id.price_subtotal
                if total_qty_in > 0.0:
                    sales_per =total_qty_out/total_qty_in * 100
                else:sales_per=0.0

                if income_qty > 0.0:
                    sales_per2 =total_qty_in/income_qty * 100
                else:sales_per2=0.0

                data.append(
                    {
                        'pro_code': pro.barcode,
                        'season_id': pro.season_id.season,
                        'year_id': pro.year_id.year,
                        'country_id': pro.country_id.manufacture,
                        'pro_name': pro.name,
                        'avalible_qty': pro.qty_available,
                        'income_qty': income_qty,
                        'income_amt': income_amt,
                        'stock': 'All',
                        'sales_qty': total_qty_in,
                        'sales_amt': total_amt_in,
                        'refund_qty': total_qty_out,
                        'refund_amt': total_amt_out,
                        'net_qty': total_qty_in - total_qty_out,
                        'net_amt': total_amt_in - total_amt_out,
                        'sales_per': round(sales_per,2),
                        'sales_per2': round(sales_per2,2),


                    }
                )

        else:
            for stock in self.stock_ids:
                locations = self.env['stock.location'].search(
                    [('location_id', 'child_of', stock.mapped('view_location_id').ids)])

                for pro in products:
                    avalible_qty = pro.with_context(warehouse=stock.id).qty_available

                    pos_lines = self.env['pos.order.line'].sudo().search([
                        ('order_id.picking_type_id.default_location_src_id', 'in', locations.ids),
                        ('product_id', '=', pro.id),
                    ])
                    total_qty_in = 0.0
                    total_qty_out = 0.0
                    total_amt_in = 0.0
                    total_amt_out = 0.0
                    for line in pos_lines:
                        if line.price_subtotal >= 0.0:
                            total_qty_in += line.qty
                            total_amt_in += line.price_subtotal
                        else:
                            total_qty_out += abs(line.qty)
                            total_amt_out += abs(line.price_subtotal)

                    move_sales_in = self.env['stock.move'].sudo().search([
                        ('picking_type_id.warehouse_id', 'in', stock.ids),
                        ('product_id', '=', pro.id),
                        ('sale_line_id', '!=', False), ('picking_code', '=', 'outgoing')
                    ])
                    move_sales_out = self.env['stock.move'].sudo().search([
                        ('picking_type_id.warehouse_id', 'in', stock.ids),
                        ('product_id', '=', pro.id),
                        ('sale_line_id', '!=', False), ('picking_code', '=', 'incoming')
                    ])

                    move_purchase = self.env['stock.move'].sudo().search([
                        ('picking_type_id.warehouse_id', 'in', stock.ids),
                        ('product_id', '=', pro.id),
                        ('purchase_line_id', '!=', False), ('picking_code', '=', 'incoming')
                    ])

                    for move in move_sales_in:
                        price = move.product_uom_qty * move.sale_line_id.price_unit
                        net_price = price - (price * move.sale_line_id.discount / 100.0)
                        total_qty_in += move.product_uom_qty
                        total_amt_in += net_price
                    for move in move_sales_out:
                        price = move.product_uom_qty * move.sale_line_id.price_unit
                        net_price = price - (price * move.sale_line_id.discount / 100.0)
                        total_qty_out += move.product_uom_qty
                        total_amt_out += net_price

                    income_qty = 0.0
                    income_amt = 0.0
                    for move in move_purchase:
                        income_qty += move.product_uom_qty
                        income_amt += move.purchase_line_id.price_subtotal
                    if total_qty_in > 0.0:
                        sales_per = total_qty_out / total_qty_in * 100
                    else:
                        sales_per = 0.0

                    if income_qty > 0.0:
                        sales_per2 = total_qty_in / income_qty * 100
                    else:
                        sales_per2 = 0.0

                    data.append(
                        {
                            'pro_code': pro.barcode,
                            'season_id': pro.season_id.season,
                            'year_id': pro.year_id.year,
                            'country_id': pro.country_id.manufacture,
                            'pro_name': pro.name,
                            'avalible_qty': avalible_qty,
                            'income_qty': income_qty,
                            'stock': stock.name,
                            'income_amt': income_amt,
                            'sales_qty': total_qty_in,
                            'sales_amt': total_amt_in,
                            'refund_qty': total_qty_out,
                            'refund_amt': total_amt_out,
                            'net_qty': total_qty_in - total_qty_out,
                            'net_amt': total_amt_in - total_amt_out,
                            'sales_per': round(sales_per, 2),
                            'sales_per2': round(sales_per2, 2),

                        }
                    )



        return data




    def generate_report(self):
        self.ensure_one()
        workbook = xlwt.Workbook()
        TABLE_HEADER = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 200;'
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
        TABLE_HEADER_payslib = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour silver_ega, pattern_back_colour silver_ega'
        )
        TABLE_HEADER_Data = TABLE_HEADER
        TABLE_HEADER_Data.num_format_str = '#,##0.00_);(#,##0.00)'
        STYLE_LINE = xlwt.easyxf(
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin; '
            'pattern: pattern solid, pattern_fore_colour silver_ega, pattern_back_colour silver_ega'
        )
        STYLE_Description_LINE = xlwt.easyxf(
            'borders:   top thin;'
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'pattern: pattern solid, pattern_fore_colour tan, pattern_back_colour tan'
        )
        TABLE_data = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index black,height 150;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour white, pattern_back_colour white'
        )
        TABLE_data.num_format_str = '#,##0.00'
        TABLE_HEADER_batch.num_format_str = '#,##0.00'
        xlwt.add_palette_colour("gray11", 0x11)
        workbook.set_colour_RGB(0x11, 222, 222, 222)
        TABLE_data_tolal_line = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index white,height 200;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour blue_gray, pattern_back_colour blue_gray'
        )

        TABLE_data_tolal_line.num_format_str = '#,##0.00'
        STYLE_Description_LINE.num_format_str = '#,##0.00'
        TABLE_data_o = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index black,height 150;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour gray11, pattern_back_colour gray11'
        )
        STYLE_LINE_Data = STYLE_LINE
        STYLE_LINE_Data.num_format_str = '#,##0.00_);(#,##0.00)'

        worksheet = workbook.add_sheet(_('Payment Plan'))
        lang = self.env.user.lang
        # if lang == "ar_SY":
        worksheet.cols_right_to_left = 1

        worksheet.col(0).width = 256 * 20
        worksheet.col(1).width = 256 * 20
        worksheet.col(2).width = 256 * 15
        worksheet.col(3).width = 256 * 15
        worksheet.col(4).width = 256 * 15
        worksheet.col(5).width = 256 * 15
        worksheet.col(6).width = 256 * 15
        worksheet.col(7).width = 256 * 15
        worksheet.col(8).width = 256 * 15
        worksheet.col(9).width = 256 * 15
        worksheet.col(10).width = 256 * 15
        worksheet.col(11).width = 256 * 15
        worksheet.col(13).width = 256 * 15
        worksheet.col(13).width = 256 * 15
        row = 0
        col = 0
        worksheet.write_merge(row, row+1, col, col + 8, _('تقرير المخزن للاصناف'), TABLE_HEADER_Data)

        row +=3
        data_lines = self.get_report_data()
        print("data_lines ==> ",data_lines)

        col = 0
        worksheet.write(row, col, _("رقم الصنف"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("اسم الصنف"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("المخزن"), TABLE_HEADER_payslib)
        col += 1
        if self.lot_ids:
            worksheet.write(row, col, _("رقم الدفعة"), TABLE_HEADER_payslib)
            col += 1
        worksheet.write(row, col, _("الموسم"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _(" البلد"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _(" السنة"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("الكمية المتوفرة"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("صافي الوارد"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("الكمية المباعة"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("مبلغ المبيعات"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("الكمية المرتجعة"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("مبلغ المردود "), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("صافي المبيعات"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("صافي المبلغ"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("نسبة المرتجع من المباع"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("معدل البيع من الوارد"), TABLE_HEADER_payslib)

        row +=1
        for line in data_lines:

            col =0
            worksheet.write(row, col, line['pro_code'] or '', TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['pro_name'] or '', TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['stock'] or '', TABLE_HEADER_batch)
            col += 1
            if self.lot_ids:

                worksheet.write(row, col, line['lot'] or '', TABLE_HEADER_batch)
                col += 1

            worksheet.write(row, col, line['season_id'] or '', TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['country_id'] or '', TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['year_id'] or '', TABLE_HEADER_batch)
            col += 1

            worksheet.write(row, col, line['avalible_qty'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['income_qty'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['sales_qty'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['sales_amt'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['refund_qty'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['refund_amt'], TABLE_HEADER_batch)
            col += 1


            worksheet.write(row, col, line['net_qty'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['net_amt'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col,'%' + str(line['sales_per']), TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col,'%' + str(line['sales_per2']) , TABLE_HEADER_batch)
            col += 1


            row +=1







        row +=1
        #
        # output = BytesIO()
        # workbook.save(output)
        # xls_file_path = (_('Items Report.xls'))
        # attachment_model = self.env['ir.attachment']
        # attachment_model.search([('res_model', '=', 'items.report.wizard'), ('res_id', '=', self.id)]).unlink()
        # attachment_obj = attachment_model.create({
        #     'name': xls_file_path,
        #     'res_model': 'items.report.wizard',
        #     'res_id': self.id,
        #     'type': 'binary',
        #     'db_datas': base64.b64encode(output.getvalue()),
        # })
        #
        # output.close()
        # url = '/web/content/%s/%s' % (attachment_obj.id, xls_file_path)
        # print("url ==> ",url)
        # return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}

        if data_lines:
            output = BytesIO()
            workbook.save(output)
            self.excel_sheet_name = 'Items Report'

            self.excel_sheet = base64.b64encode(output.getvalue())
            self.excel_sheet_name = str(self.excel_sheet_name) + '.xls'
            output.close()
            return {
                'type': 'ir.actions.act_url',
                'name': 'POS Target Report',
                'url': '/web/content/items.report.wizard/%s/excel_sheet/Items Report.xls?download=true' % (
                    self.id),
                'target': 'self'
            }
        else:
            view_action = {
                'name': _('Items Report'),
                'view_mode': 'form',
                'res_model': 'items.report.wizard',
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new',
                'context': self.env.context,
            }

            return view_action






