# -*- coding: utf-8 -*-
import pytz
from odoo import fields, models, api, _
from datetime import datetime , date ,timedelta
import calendar
class pos_target_line(models.Model):
    _name = 'pos.target.line'
    _rec_name = 'pos_config_id'
    _description = 'POS Target Line'
    pos_config_id = fields.Many2one(comodel_name="pos.config", string="Point Of Sale", required=True, )
    amount = fields.Float(string="Amount",  required=True, )
    target_id = fields.Many2one(comodel_name="pos.target", string="Target", required=False, )
    start_date = fields.Date(related='target_id.start_date',store=True )
    end_date = fields.Date(related='target_id.end_date' , store=True)



class pos_target(models.Model):
    _name = 'pos.target'
    _rec_name = 'name'
    _description = 'POS Target'

    name = fields.Char()
    # display_name = fields.Char(compute="_compute_display_name", store=True)
    start_date = fields.Date(string='Start Date', required=True, default=str(datetime.today().replace(day=1)))
    end_date = fields.Date(required=True, default=str(datetime.now().replace(day = calendar.monthrange(datetime.now().year, datetime.now().month)[1])))
    target_line_ids = fields.One2many(comodel_name="pos.target.line", inverse_name="target_id", string="Target Lines", required=False, )


# @api.multi
    # @api.depends('name','pos_config_id')
    # def _compute_display_name(self):
    #     for rec in self:
    #         if rec.name:
    #             rec.display_name = rec.name
    #             if rec.pos_config_id.name:
    #                 rec.display_name= rec.name + '( ' + rec.pos_config_id.name + ' )'
    #         elif rec.pos_config_id.name:
    #             rec.display_name = rec.pos_config_id.name
    #         else:rec.display_name =''
