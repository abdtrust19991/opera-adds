# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class NameModel(models.TransientModel):
    _name = 'pos.session.close.wizard'

    entered_password = fields.Char(string="Password")

    def confirm_action(self):
        session_id = self.env.context.get('session_id',False) or self.env.context.get('active_id')
        session = self.env['pos.session'].browse(session_id)
        config_password = session.config_id.change_cashier_pwd
        if self.entered_password == config_password:
            if not self.env.context.get('validate',False):
                session.action_pos_session_closing_control()
            else:
                session.action_pos_session_validate()
        else:
            raise ValidationError(_("Wrong Password"))
