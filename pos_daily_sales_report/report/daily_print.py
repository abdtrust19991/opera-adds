# -*- coding: utf-8 -*-

#############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class PosDailyPrint(models.AbstractModel):
    _name = 'report.pos_daily_sales_report.daily_sales_doc'

    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        print("data",data)
        return data