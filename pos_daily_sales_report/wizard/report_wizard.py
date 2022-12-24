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
import pytz
from pytz import timezone
import logging
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class PosDailyReportWizard(models.TransientModel):
    _name = 'daily.report.wizard'


    start_date = fields.Date(default=fields.Date.today(),required=True, )
    end_date = fields.Date(default=fields.Date.today(),required=True, )

    user_id = fields.Many2one(comodel_name="res.users", string="Pos User",default=lambda self:self.env.user, required=True, )
    pos_config_id = fields.Many2one(comodel_name="pos.config", string="Point Of Sale", required=True, )

    session_id = fields.Many2one('pos.session')


    @api.onchange('user_id','start_date','end_date')
    def onchange_user_id(self):
        if self.user_id:
            pos = []
            tz = timezone(self.env.user.tz)
            date_from = tz.localize(
                datetime.datetime.combine(fields.Datetime.from_string(str(self.start_date)), time.min))
            date_to = tz.localize(datetime.datetime.combine(fields.Datetime.from_string(str(self.end_date)), time.max))
            pos_ids = self.env['pos.session'].search([('user_id','=',self.user_id.id),('start_at', '>=', date_from),'|',('stop_at', '=', False), ('stop_at', '<=', date_to)])
            for rec in pos_ids:
                if rec.config_id.id not in pos:
                    pos.append(rec.config_id.id)
            if pos:
                self.pos_config_id = pos[0]
            domain = [('id','in',pos)]
            return {'domain': {'pos_config_id': domain,'session_id':[('id','=',pos_ids.ids)]}}


    def get_report_data(self):
        print("get_report_data ")

        tz = timezone(self.env.user.tz)
        date_from = tz.localize(datetime.datetime.combine(fields.Datetime.from_string(str(self.start_date)), time.min))
        date_to = tz.localize(datetime.datetime.combine(fields.Datetime.from_string(str(self.end_date)), time.max))
        domain =[('order_id.date_order', '>=', date_from), ('order_id.date_order', '<=', date_to),('order_id.config_id', '=', self.pos_config_id.id)]
        if self.session_id:
            domain += [('order_id.session_id', '=', self.session_id.id)]
            session = self.session_id.name
        else:
            session = 'All'
        orders = self.env['pos.order.line'].search(domain)
        print("date_from ===> ", date_from)
        print("date_to ===> ", date_to)
        print("orders ===> ", orders)
        qty_sal = 0.0
        qty_rt = 0.0
        amt_sal = 0.0
        amt_rt = 0.0
        tax_amt = 0.0
        payments = {}
        total_pay=0.0
        cash=0.0
        pay_lst=[]

        for rec in orders:
            if rec.qty > 0.0:
                qty_sal += rec.qty
                amt_sal += rec.price_subtotal_incl
                tax_amt += (rec.price_subtotal_incl - rec.price_subtotal)
            if rec.qty < 0.0:
                qty_rt += abs(rec.qty)
                amt_rt += abs(rec.price_subtotal_incl)
                tax_amt -= (abs(rec.price_subtotal_incl) - abs(rec.price_subtotal))
            for pay in rec.order_id.payment_ids:
                if pay not in pay_lst:
                    pay_lst.append(pay)

        for pay in pay_lst:
            method = pay.payment_method_id.name
            if pay.payment_method_id.method_cash:
                cash += pay.amount
                continue
            total_pay += pay.amount
            if method in payments:
                payments[method] += pay.amount
            else:
                payments[method] = pay.amount
        data = {
            'date_from' : self.start_date,
            'date_to' : self.end_date,
            'user' : self.user_id.login,
            'session' : session,
            'pos':self.pos_config_id.name,
            'amt_sal':amt_sal,
            'qty_sal':qty_sal,
            'qty_rt':qty_rt,
            'net_qty':qty_sal - qty_rt,
            'amt_rt':amt_rt,
            'payments':payments,
            'cash':cash,
            'total_pay':total_pay,
            'total_untax':amt_sal - amt_rt - tax_amt,
            'tax_amt':tax_amt,
            'total':amt_sal - amt_rt ,

        }
        return data


    def action_print_pdf(self):
        data = self.get_report_data()
        print("data => ",data)
        return self.env.ref('pos_daily_sales_report.report_pos_daily_sales').report_action([], data=data)




