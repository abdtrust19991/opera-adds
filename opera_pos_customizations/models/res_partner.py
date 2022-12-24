# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_pos_customer = fields.Boolean()

    @api.model
    def create_from_ui(self, values):
        values['is_pos_customer'] = True
        partner = super(ResPartner, self).create_from_ui(values)
        return partner

