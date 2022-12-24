# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class UOM(models.Model):
    _inherit = 'uom.uom'

    disable_fraction = fields.Boolean()
