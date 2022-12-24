# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    pos_code = fields.Char(string="Point Of Sale Code",
                           help="This is the code used for sales persons in point of sale")
