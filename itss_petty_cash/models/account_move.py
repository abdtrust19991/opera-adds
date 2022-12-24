# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
#
# ##############################################################################
# #
# #
# #    Copyright (C) 2018-TODAY .
# #    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
# #
# #    It is forbidden to publish, distribute, sublicense, or sell copies
# #    of the Software or modified copies of the Software.
# #
# ##############################################################################
import time
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    petty_id=fields.Many2one('petty.cash','Petty Cash')
    petty_cash_ids = fields.Many2many(comodel_name="petty.cash", relation="rel_petty_move", column1="petty_cash", column2="petty_pement", string="Petty Cash", )

