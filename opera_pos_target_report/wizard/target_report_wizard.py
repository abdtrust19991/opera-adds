# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _
import pytz
import xlwt
import odoo.osv.osv
import re
import base64
import io
from io import BytesIO
import datetime
from datetime import date, time
from pytz import timezone
import pytz

import logging
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class PosTargetReportWizard(models.TransientModel):
    _name = 'pos.target.report.wizard'


    def _default_start_date(self):
        """ Find the earliest start_date of the latests sessions """
        # restrict to configs available to the user
        config_ids = self.env['pos.config'].search([]).ids
        # exclude configs has not been opened for 2 days
        self.env.cr.execute("""
            SELECT
            max(start_at) as start,
            config_id
            FROM pos_session
            WHERE config_id = ANY(%s)
            AND start_at > (NOW() - INTERVAL '2 DAYS')
            GROUP BY config_id
        """, (config_ids,))
        latest_start_dates = [res['start'] for res in self.env.cr.dictfetchall()]
        # earliest of the latest sessions
        return latest_start_dates and min(latest_start_dates) or fields.Datetime.now()

    start_date = fields.Date()
    end_date = fields.Date()
    target_id = fields.Many2one(comodel_name="pos.target", string="Target", required=True, )
    report_type = fields.Selection(string="Report Type",default="xls", selection=[('xls', 'XLS'), ('html', 'HTML'), ], required=True, )



    excel_sheet = fields.Binary('Download Report')
    excel_sheet_name = fields.Char(string='Name', size=64)


    @api.onchange('start_date')
    def _onchange_start_date(self):
        for rec in self.target_id:
            if self.start_date < rec.start_date:
                self.start_date = rec.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        for rec in self.target_id:
            if self.end_date > rec.end_date:
                self.end_date = rec.end_date



    def action_print(self):
        if self.report_type == 'xls':
            return self.action_print_xls()

        elif self.report_type == 'html':
            return self.action_print_html()

    def get_days(self):
        if self.start_date:
            start = self.start_date
        else:
            start = self.target_id.start_date
        if self.end_date:
            end = self.end_date
        else:
            end = self.target_id.end_date

        step = datetime.timedelta(days=1)
        lst_days = []
        x = 1
        while start <= end:
            m = start.strftime("%B")
            d = start.strftime('%d')
            name = str(d) + '-' + m
            lst_days.append(name)
            start += step

            x += 1
        return lst_days

    def get_target(self):
        branches=[]
        for rec in self.target_id.target_line_ids:
            if self.start_date:
                start = self.start_date
            else:
                start = rec.start_date
            if self.end_date:
                end = self.end_date
            else:
                end = rec.end_date

            tz = timezone(self.env.user.tz)

            print("end  1==> ",end)
            print("start 1==> ",start)
            print("end 2==> ",rec.end_date)
            print("start 2 ==> ",rec.start_date)
            target_delta = rec.end_date - rec.start_date
            print(target_delta.days)
            target_num_days = target_delta.days +1
            target_day = rec.amount/target_num_days
            target_amount = rec.amount
            print("target_day ==>> ",target_num_days)
            step = datetime.timedelta(days=1)
            total_sales = 0.0
            lst_days=[]
            sel_delta = end - start
            sel_num_days = sel_delta.days +1
            print("sel_num_days ===> ", sel_num_days)
            while start <= end:
                print("date ===> ",start)
                date_from = tz.localize(datetime.datetime.combine(fields.Datetime.from_string(str(start)), time.min))
                date_to = tz.localize(datetime.datetime.combine(fields.Datetime.from_string(str(start)), time.max))
                orders = self.env['pos.order'].search([('date_order','>=',date_from),('date_order','<=',date_to),('config_id','=',rec.pos_config_id.id)])
                print("date_from ===> ",date_from)
                print("date_to ===> ",date_to)
                print("orders ===> ",orders)

                day_total = 0.0
                for line in orders:
                    day_total += line.amount_total
                if target_num_days<=0:
                    day_target = target_amount
                else:
                    day_target = target_amount/target_num_days
                print("target_num_days ===> ",target_num_days)
                print("target_amount ===> ",target_amount)
                print("day_target ===> ",day_target)
                target_num_days -=1
                target_amount -=day_total
                total_sales +=day_total
                lst_days.append(
                    {
                     'date':str(start),
                     'day_total':day_total,
                     'day_target':day_target,
                    }
                    )


                start +=step
            net = rec.amount - total_sales
            over_target =0.0
            rem_target =0.0
            if net<0.0:
                over_target = total_sales - rec.amount
            else:rem_target= net
            avg=total_sales/sel_num_days
            run_ret = round(int(target_delta.days+1) * avg,2)
            branches.append({
                'name':rec.pos_config_id.name,
                'user':self.env.user.name,
                'target_amount':rec.amount,
                'total_sales':total_sales,
                'rem_target':rem_target,
                'over_target':over_target,
                'sale_percent':round(total_sales/rec.amount *100,2),
                'avg_sales_day':round(avg,2) ,
                'run_ret': run_ret  ,
                'run_ret_per': round(run_ret/rec.amount * 100 ,2) ,
                'lst_days':lst_days,
                'currant':self.get_daily_target(lst_days),

            }

            )
        return branches

    def get_daily_target(self,days_lst):
        currant = self.start_date or fields.Date.today()
        for line in days_lst:
            if line['date'] == str(currant):
                return line

    def action_print_xls(self):
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
        worksheet.col(2).width = 256 * 20
        worksheet.col(3).width = 256 * 20
        worksheet.col(4).width = 256 * 20
        worksheet.col(5).width = 256 * 20
        worksheet.col(6).width = 256 * 20
        worksheet.col(7).width = 256 * 15
        worksheet.col(8).width = 256 * 15
        worksheet.col(9).width = 256 * 15
        worksheet.col(10).width = 256 * 15
        row = 0
        col = 0
        worksheet.write_merge(row, row+1, col, col + 4, _('POS Target Report'), TABLE_HEADER_Data)

        row +=2
        data_lines = self.get_target()
        print("data_lines ==> ",data_lines)

        col = 0
        worksheet.write(row, col, _("Branch Name"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("Showroom Manager"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("Target Of Month"), TABLE_HEADER_payslib)

        # row +=
        col += 1
        lst_days = self.get_days()
        for day in lst_days:

            worksheet.write_merge(row,row,col, col+1, day, TABLE_data)
            col +=2


        worksheet.write(row, col, _("Total sales"), TABLE_HEADER_payslib)
        col +=1
        worksheet.write(row, col, _("Remain For Target"), TABLE_HEADER_payslib)
        col +=1
        worksheet.write(row, col, _("Over Target"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("Sales %"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("Average Daily Sales"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("Run rate"), TABLE_HEADER_payslib)
        col +=1
        worksheet.write(row, col, _("Run rate%"), TABLE_HEADER_payslib)
        row +=1
        col = 3
        for day in lst_days:
            worksheet.write(row, col, _("Daily Target"), TABLE_HEADER_payslib)
            col+=1
            worksheet.write(row, col, _("Sales"), TABLE_HEADER_payslib)
            col+=1
        row +=1
        for line in data_lines:
            col =0
            worksheet.write(row, col, line['name'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['user'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['target_amount'], TABLE_HEADER_batch)
            col += 1
            for day in line['lst_days']:

                worksheet.write(row, col, day['day_target'], TABLE_data)
                col +=1
                worksheet.write(row, col, day['day_total'], TABLE_data)
                col +=1

            worksheet.write(row, col, line['total_sales'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['rem_target'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['over_target'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col,  '%' + str(line['sale_percent']), TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['avg_sales_day'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col,line['run_ret'], TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, '%' + str(line['run_ret_per']), TABLE_HEADER_batch)
            col += 1

            row +=1


        col = 0
        row +=1
        if data_lines:
            output = BytesIO()
            workbook.save(output)
            self.excel_sheet_name = 'POS Target Report'

            self.excel_sheet = base64.b64encode(output.getvalue())
            self.excel_sheet_name = str(self.excel_sheet_name) + '.xls'
            output.close()
            return {
                'type': 'ir.actions.act_url',
                'name': 'POS Target Report',
                'url': '/web/content/pos.target.report.wizard/%s/excel_sheet/POS Target Report.xls?download=true' % (
                    self.id),
                'target': 'self'
            }
        else:
            view_action = {
                'name': _(' Vendor Payment Report'),
                'view_mode': 'form',
                'res_model': 'pos.target.report.wizard',
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new',
                'context': self.env.context,
            }

            return view_action

        # output = BytesIO()
        # workbook.save(output)
        # xls_file_path = (_('Pos Target.xls'))
        # attachment_model = self.env['ir.attachment']
        # attachment_model.search([('res_model', '=', 'pos.target.report.wizard'), ('res_id', '=', self.id)]).unlink()
        # attachment_obj = attachment_model.create({
        #     'name': xls_file_path,
        #     'res_model': 'pos.target.report.wizard',
        #     'res_id': self.id,
        #     'type': 'binary',
        #     'db_datas': base64.b64encode(output.getvalue()),
        # })
        #
        # output.close()
        # url = '/web/content/%s/%s' % (attachment_obj.id, xls_file_path)
        # print("url ==> ",url)
        # return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}

    def action_print_html(self):
        data={}
        resalt = self.get_target()
        data['data']=resalt
        print("data 88=> ", data)
        return self.env.ref('opera_pos_target_report.target_sales_report').report_action([], data=data)


