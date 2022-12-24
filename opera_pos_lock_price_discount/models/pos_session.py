# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'


    def action_pos_session_closing_control_mod(self):

        if self.config_id.lock_change_cashier:
            view_action = {
                'name': _(' Enter Password '),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pos.session.close.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
            return view_action
        else:
            return self.with_context(session_id=self.id).action_pos_session_closing_control()

    def action_pos_session_validate_mod(self):
        if self.config_id.lock_change_cashier:
            context = dict(self.env.context)
            context.update({'validate': True, 'session_id': self.id})
            view_action = {
                'name': _(' Enter Password '),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pos.session.close.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': context,
            }
            return view_action
        else:
            return self.action_pos_session_validate()