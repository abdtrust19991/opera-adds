# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today  Technaureus Info Solutions Pvt.Ltd.(<http://technaureus.com/>)
from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    fixed_limit = fields.Float(string="Fixed Limit")
    percentage_limit = fields.Float(string="Percentage Limit")


