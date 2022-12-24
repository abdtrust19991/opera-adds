# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class PosOrderInherit(models.Model):
	_inherit = 'pos.order'

	return_order_ref = fields.Many2one('pos.order',string="Return Order Ref")

	def _order_fields(self, ui_order):
		res = super(PosOrderInherit, self)._order_fields(ui_order)
		if 'return_order_ref' in ui_order:
			if ui_order.get('return_order_ref') != False:
				res['return_order_ref'] = int(ui_order['return_order_ref'])
				po_line_obj = self.env['pos.order.line']
				for l in ui_order['lines']:
					line = po_line_obj.browse(int(l[2]['original_line_id']))
					if line:
						line.write({
							'return_qty' : line.return_qty - (l[2]['qty']),
						})
		return res


class PosOrderLineInherit(models.Model):
	_inherit = 'pos.order.line'

	original_line_id = fields.Many2one('pos.order.line', string="original Line")
	return_qty = fields.Float('Return Qty')