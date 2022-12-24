# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sale_persons_ids = fields.Many2many(
        'hr.employee',
        'check_sale_persons_rel',
        'check_sale_persons_id',
        'sale_persons_id')

    default_employee_id = fields.Many2one(
        'hr.employee',
        default=lambda self:self.env['hr.employee'].search([], limit=1)
    )
