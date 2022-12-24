# -*- coding: utf-8 -*-

from odoo import models,api

class theme_utils(models.AbstractModel):
    _inherit = 'theme.utils'

    @api.model
    def _reset_default_config(self):
        super()._reset_default_config()
        # custom header
        self.disable_view('theme_alan.header_layout_1')
        self.disable_view('theme_alan.header_layout_2')
        self.disable_view('theme_alan.header_layout_3')
        self.disable_view('theme_alan.header_layout_4')
        self.disable_view('theme_alan.header_layout_5')
        self.disable_view('theme_alan.header_layout_6')
        self.disable_view('theme_alan.header_layout_7')
        self.disable_view('theme_alan.header_layout_8')
        self.disable_view('theme_alan.header_layout_9')
        # custom footer
        self.disable_view('theme_alan.footer_layout_1')
        self.disable_view('theme_alan.footer_layout_2')
        self.disable_view('theme_alan.footer_layout_3')
        self.disable_view('theme_alan.footer_layout_4')
        self.disable_view('theme_alan.footer_layout_5')
        self.disable_view('theme_alan.footer_layout_6')
        self.disable_view('theme_alan.footer_layout_7')
        self.disable_view('theme_alan.footer_layout_8')
