# -*- coding: utf-8 -*-

from odoo import api, fields, models, _,exceptions
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ResDrive(models.Model):
    _name = 'res.driver'
    name = fields.Char(string="Nem", required=True, )


class stockpicking(models.Model):
    _inherit = 'stock.picking'

    driver_id = fields.Many2one(comodel_name="res.driver", string="Driver Person", required=False, )
