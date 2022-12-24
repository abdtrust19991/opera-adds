# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _


class pos_config(models.Model):
    _inherit = 'pos.config'

    pos_branch_id = fields.Many2one(comodel_name="pos.branch",)
