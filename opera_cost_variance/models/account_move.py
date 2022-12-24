# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    cost_variance_id = fields.Many2one(
        'cost.variance'
    )

    def action_post(self):
        """ Override action_post """
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.cost_variance_id:
                rec.cost_variance_id.write({
                    'state': 'posted'
                })
        return res