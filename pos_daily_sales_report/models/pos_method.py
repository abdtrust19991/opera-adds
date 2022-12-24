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
class pos_payment_method(models.Model):
    _inherit = 'pos.payment.method'

    method_cash = fields.Boolean(string="Method Cash",  )


class pos_session(models.Model):
    _inherit = 'pos.session'

    def get_report_data(self):
        print("get_report_data ")

        tz = timezone(self.env.user.tz)
        # date_from = tz.localize(datetime.datetime.combine(fields.Datetime.from_string(str(self.start_date)), time.min))
        # date_to = tz.localize(datetime.datetime.combine(fields.Datetime.from_string(str(self.end_date)), time.max))
        domain = [
                  ('order_id.config_id', '=', self.config_id.id),('order_id.session_id', '=', self.id)]
        session = self.name

        orders = self.env['pos.order.line'].search(domain)

        print("orders ===> ", orders)
        qty_sal = 0.0
        qty_rt = 0.0
        amt_sal = 0.0
        amt_rt = 0.0
        tax_amt = 0.0
        payments = {}
        total_pay = 0.0
        cash = 0.0
        pay_lst = []

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
            'date_from': self.start_at.date(),
            'date_to': self.stop_at.date(),
            'user': self.activity_user_id.login,
            'session': session,
            'pos': self.config_id.name,
            'amt_sal': amt_sal,
            'qty_sal': qty_sal,
            'qty_rt': qty_rt,
            'net_qty': qty_sal - qty_rt,
            'amt_rt': amt_rt,
            'payments': payments,
            'cash': cash,
            'total_pay': total_pay,
            'total_untax': amt_sal - amt_rt - tax_amt,
            'tax_amt': tax_amt,
            'total': amt_sal - amt_rt,

        }
        return data

    def action_pos_session_closing_control(self):
        super(pos_session, self).action_pos_session_closing_control()
        data = self.get_report_data()
        return self.env.ref('pos_daily_sales_report.report_pos_daily_sales').report_action([], data=data)
    def action_pos_session_validate(self):
        super(pos_session, self).action_pos_session_validate()
        data = self.get_report_data()
        return self.env.ref('pos_daily_sales_report.report_pos_daily_sales').report_action([], data=data)





    # def _validate_session(self):
    #     print(" **** Closing *****")
    #     super(pos_session, self)._validate_session()
    #     data = self.get_report_data()
    #     print("data => ")
    #     print("data => ", data)
    #     return self.env.ref('pos_daily_sales_report.report_pos_daily_sales').report_action([], data=data)
    #
    #     # return rec , report
