# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    apply_discount_limit = fields.Boolean(default=True  )
    discount_limit = fields.Float(default=20,string="Discount Limit (%)" )


