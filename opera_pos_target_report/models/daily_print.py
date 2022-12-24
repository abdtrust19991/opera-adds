# -*- coding: utf-8 -*-

#############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class PosTargetPrint(models.AbstractModel):
    _name = 'report.opera_pos_target_report.target_sales_doc'

    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        print("data555",data)
        return data