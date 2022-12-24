# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models
from collections import defaultdict



class planReportXls(models.AbstractModel):
    _name = 'report.purchase_plan.plan_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'


    def get_total(self, data):
        lines = []
        p_total_amount=0.0
        p_total_qty=0.0
        a_total_amount = 0.0
        a_total_qty = 0.0

        for line in data:
            p_total_amount += line.p_total
            p_total_qty +=  line.p_qty
            a_total_amount += line.a_total
            a_total_qty += line.a_qty

        dif_amount= p_total_amount - a_total_amount
        dif_qty= p_total_qty - a_total_qty
        if p_total_amount!=0.0:
            ret_amount = a_total_amount/p_total_amount *100
        else:ret_amount=0.0
        if p_total_qty != 0.0:
            ret_qty = a_total_qty / p_total_qty * 100
        else:
            ret_qty = 0.0
        rec ={
             'p_total_amount':p_total_amount,
             'p_total_qty':p_total_qty,
             'a_total_amount':a_total_amount,
             'a_total_qty':a_total_qty,
             'dif_amount':dif_amount,
             'dif_qty':dif_qty,
             'ret_amount':dif_qty,
             'ret_qty':dif_qty,

         }
        return rec



    def get_color(self,plan_id):
        lst_color=[]
        lst_factory = []
        fact = []
        c = defaultdict(int)
        lst_temp=[]
        lst_co=[]
        lst = defaultdict(int)
        res = self.env['purchase.order'].search([('plan_id','=',plan_id)])
        for rec in res:
            for line in rec.order_line:
                if line.color:
                    if line.product_id.product_tmpl_id.id not in lst_temp or line.color.name not in lst_co:
                        co={
                            'color':line.color.name,
                            'No':1,
                        }
                        lst_temp.append(line.product_id.product_tmpl_id.id)
                        lst_co.append(line.color.name)
                        lst_color.append(co)
                if line.factory:
                    res={
                        'factory':line.factory.name,
                        'amount':line.price_subtotal,
                        'qty':line.product_qty,
                        'model_qty':line.model_no,
                        'templ':line.product_id.product_tmpl_id.id,
                    }
                    lst_factory.append(res)

        if lst_factory:

            fact =[{'factory':lst_factory[0]['factory'],'amount':0.0,'qty':0.0,'model_qty':0}]
            pro_lst=[]
            for d in lst_factory:

                flag = False
                for f in fact:
                    if d['factory'] == f['factory']:
                        f['amount'] += d['amount']
                        f['qty'] += d['qty']
                        f['templ'] = d['templ']
                        if f['templ'] not in pro_lst:
                            pro_lst.append(f['templ'])
                            f['model_qty'] += 1

                        flag =False
                        break
                    else:
                        flag=True
                if flag:
                    fact.append(d)
        if lst_color:
            for co in lst_color:
                lst[co['color']] += co['No']
        lst_color =[{'color': name, 'No': qty} for name, qty, in lst.items()]

        return {'color':lst_color,'factory':fact}
    def generate_xlsx_report(self, workbook, data, lines):
        plan_number=data['form']['number']
        plan_date=data['form']['date']
        plan_ids=data['form']['plan_line_ids']
        plan_id=data['form']['id']
        plan_lines=self.env['purchase.plan.line'].browse(plan_ids)
        comp = self.env.user.company_id.name
        sheet = workbook.add_worksheet('plan')
        format0 = workbook.add_format({'font_size': 18, 'align': 'center','bg_color': '#999999', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bg_color': '#999999','bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 12,'top': True, 'align': 'center','bg_color': '#999999', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
        red_mark = workbook.add_format({'font_size': 12,'bold': True })
        justify = workbook.add_format({'font_size': 12})
        format3.set_align('center')
        format21.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')
        sheet.merge_range(1, 2, 2, 7, 'Purchase Plan Report', format0)
        sheet.merge_range(3, 2, 3, 7, comp, format11)
        sheet.merge_range(7,2,5,7, 'Plan Information', format1)
        w_col_no = 6
        w_col_no1 = 7
        sheet.set_column(0, 0, 20)
        sheet.set_column(0, 1, 12)
        sheet.set_column(0, 2, 12)
        sheet.set_column(0, 3, 12)
        sheet.set_column(0, 4, 12)
        sheet.set_column(0, 5, 12)
        sheet.set_column(0, 6, 12)
        sheet.set_column(0, 7, 12)
        sheet.set_column(0, 8, 12)
        sheet.set_column(0, 9, 12)
        sheet.set_column(0, 10, 12)
        sheet.set_column(0, 11, 12)

        sheet.merge_range(9, 0, 10, 0, 'Group', format21)
        sheet.merge_range(9, 1, 9, 2, 'Purchases Plan', format21)
        sheet.write(10, 1, 'P-Amount', format21)
        sheet.write(10, 2, 'P-QTY', format21)
        sheet.merge_range(9, 3, 9, 4, 'Actual Purchases', format21)
        sheet.write(10, 3, 'A-Amount', format21)
        sheet.write(10, 4, 'A-QTY', format21)
        sheet.merge_range(9, 5, 9, 6, 'Differential', format21)
        sheet.write(10, 5, 'D-Amount', format21)
        sheet.write(10, 6, 'D-QTY', format21)
        sheet.merge_range(9, 7, 9, 8, 'Ratio', format21)
        sheet.write(10, 7, 'R-Amount', format21)
        sheet.write(10, 8, 'R-QTY', format21)
        sheet.merge_range(9, 9, 9, 12, 'Model QTY', format21)
        sheet.write(10, 9, 'M-Plan', format21)
        sheet.write(10, 10, 'M-Act', format21)
        sheet.write(10, 11, 'M-Diff', format21)
        sheet.write(10, 12, 'M-Ratio', format21)
        prod_row = 11


        for line in plan_lines:
            sheet.write(prod_row, 0, line.category_id.display_name, red_mark)
            sheet.write(prod_row, 1, line.p_total, red_mark)
            sheet.write(prod_row, 2, line.p_qty, red_mark)
            sheet.write(prod_row, 3, line.a_total, red_mark)
            sheet.write(prod_row, 4, line.a_qty, red_mark)
            sheet.write(prod_row, 5, line.dif_total, red_mark)
            sheet.write(prod_row, 6, line.dif_qty, red_mark)
            sheet.write(prod_row, 7, str(line.rat_total)+'%', red_mark)
            sheet.write(prod_row, 8, str(line.rat_qty)+'%', red_mark)
            sheet.write(prod_row, 9, line.p_model_no, red_mark)
            sheet.write(prod_row, 10, line.a_model_no, red_mark)
            sheet.write(prod_row, 11, line.dif_model, red_mark)
            sheet.write(prod_row, 12, str(line.rat_model)+'%', red_mark)

            prod_row = prod_row + 1
        prod_row +=1
        m_row=prod_row+2
        sheet.merge_range(prod_row, 2, m_row, 8, 'Purchase Plan (Total)', format1)
        prod_row +=4
        sheet.write(prod_row, 3, 'Total', format21)
        sheet.write(prod_row, 4, 'Purchases Plan', format21)
        sheet.write(prod_row, 5, 'Actual Purchases', format21)
        sheet.write(prod_row, 6, 'Differential', format21)
        sheet.write(prod_row, 7, 'Ratio', format21)
        prod_row += 1
        total= self.get_total(plan_lines)

        sheet.write(prod_row, 3, 'Amount', format21)
        sheet.write(prod_row, 4, total['p_total_amount'], red_mark)
        sheet.write(prod_row, 5, total['a_total_amount'], red_mark)
        sheet.write(prod_row, 6, total['dif_amount'], red_mark)
        sheet.write(prod_row, 7, total['ret_amount'], red_mark)
        prod_row += 1
        sheet.write(prod_row, 3, 'QTY', format21)
        sheet.write(prod_row, 4, total['p_total_qty'], red_mark)
        sheet.write(prod_row, 5, total['a_total_qty'], red_mark)
        sheet.write(prod_row, 6, total['dif_qty'], red_mark)
        sheet.write(prod_row, 7, total['ret_qty'], red_mark)

        prod_row += 3
        m_row = prod_row + 2
        sheet.merge_range(prod_row, 2, m_row, 7, 'Colors And Factory', format1)
        prod_row += 4
        m_row = prod_row + 1
        sheet.merge_range(prod_row, 1, m_row, 2, 'Colors', format1)
        sheet.merge_range(prod_row, 4, m_row, 8, 'Factories', format1)
        prod_row +=2
        sheet.write(prod_row, 1, 'Color', format21)
        sheet.write(prod_row, 2, 'No', format21)
        sheet.write(prod_row, 4, 'Factory', format21)
        sheet.write(prod_row, 5, 'Amount', format21)
        sheet.write(prod_row, 6, 'Qty', format21)
        sheet.write(prod_row, 7, 'Qty-Model', format21)
        sheet.write(prod_row, 8, 'Average', format21)
        lst = self.get_color(plan_id)
        lst_color = lst['color']
        lst_factory = lst['factory']
        color_row=prod_row
        fact_row=prod_row
        for co in lst_color:

            color_row += 1
            sheet.write(color_row, 1, co['color'], red_mark)
            sheet.write(color_row, 2, co['No'], red_mark)

        for f in lst_factory:

            fact_row += 1
            sheet.write(fact_row, 4, f['factory'], red_mark)
            sheet.write(fact_row, 5, f['amount'], red_mark)
            sheet.write(fact_row, 6, f['qty'], red_mark)
            sheet.write(fact_row, 7, f['model_qty'], red_mark)
            sheet.write(fact_row, 8, round(f['amount']/f['qty'],2), red_mark)

