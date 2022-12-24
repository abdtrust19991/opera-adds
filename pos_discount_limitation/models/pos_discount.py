# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosDiscount(models.Model):

    _name = 'pos.discount.limitation'
    _rec_name = 'group_id'

    group_id = fields.Many2one('res.groups')
    pos_discount_limitation = fields.Float()


class ResGroups(models.Model):

    _inherit = "res.groups"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        context = self.env.context
        if context.get('is_pos_discount'):
            category_id = self.env.ref('base.module_category_point_of_sale')
            if category_id:
                domain = [('category_id', '=', category_id.id)]
        else:
            domain = []
        res_groups = self._search(
            domain + args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(res_groups))
