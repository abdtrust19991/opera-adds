# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

# from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging
from odoo.http import request

from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)

INTERNAL_TRANSFER_TYPE = [('request', _('Request')), ('send', _('Send'))]


class accerps_internal_transfers(models.Model):
    _inherit = 'stock.picking'

    # location_before_transit_id = fields.Many2one(
    #     'stock.location', "Destination Location Before Transit",
    #     check_company=True, readonly=True)
    # location_after_transit_id = fields.Many2one(
    #     'stock.location', "Destination Location After Transit",
    #     check_company=True, readonly=True)
    # picking_dest_id = fields.Many2one(
    #     'stock.picking', 'Destination Picking', readonly=True)

    inter_transfer_type = fields.Selection(INTERNAL_TRANSFER_TYPE, string='Internal transfer type')

    @api.onchange('inter_transfer_type')
    def onchange_inter_transfer_type(self):
        if self.picking_type_id.code == 'internal':
            if self.inter_transfer_type == 'request':
                self.location_id = False
                self.location_dest_id = self.picking_type_id.default_location_src_id

                # self.location_dest_id = False

            if self.inter_transfer_type == 'send':
                self.location_id = self.picking_type_id.default_location_src_id
                self.location_dest_id = False

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        super(accerps_internal_transfers, self).onchange_picking_type()
        if self.picking_type_id.code != 'internal':
            self.inter_transfer_type = False

    def action_confirm(self):
        res = True
        if self.picking_type_id.code == 'internal':
            if self.env.user.id in self.location_dest_id.user_ids.ids and self.create_uid.id in self.location_dest_id.user_ids.ids:
                res = super(accerps_internal_transfers, self).action_confirm()

                _message = _("The request <a href='%s'>%s</a> has been sent by %s")

                _args = (self._generate_current_form_url(), self.name, self.location_dest_id.name)
                self.send_notification_users(_message % _args,
                                             [user.partner_id.id for user in self.location_id.user_ids])

            elif self.env.user.id in self.location_id.user_ids.ids and self.create_uid.id in self.location_id.user_ids.ids:
                res = super(accerps_internal_transfers, self).action_confirm()
            else:
                member_for = [self.location_id.name, self.location_dest_id.name]
                if self.create_uid.id in self.location_dest_id.user_ids.ids:
                    member_for = [self.location_dest_id.name]
                elif self.create_uid.id in self.location_id.user_ids.ids:
                    member_for = [self.location_id.name]

                raise UserError(_("Sorry! You are not member for %s.") % (' nor '.join(member_for)))
        else:
            res = super(accerps_internal_transfers, self).action_confirm()

        return res

    def action_assign(self):
        res = True
        if self.picking_type_id.code == 'internal':
            if self.env.user.id in self.location_id.user_ids.ids:
                res = super(accerps_internal_transfers, self).action_assign()
                if self.state == 'assigned':
                    _message = ""
                    if self.inter_transfer_type in ['request']:
                        _message = _("The Request <a href='%s'>%s</a> has been confirmed by %s")
                    else:
                        _message = _("The transfer <a href='%s'>%s</a> has been sent by %s")

                    _args = (self._generate_current_form_url(), self.name, self.location_id.name)
                    self.send_notification_users(_message % _args,
                                                 [user.partner_id.id for user in self.location_dest_id.user_ids])
            else:
                raise UserError(_("Checking availability quantity accessed by location source user only."))
        else:
            res = super(accerps_internal_transfers, self).action_assign()

        return res

    def _force_set_quantity(self):
        self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]}).process()

    def check_duplicate_product_move_line(self, lines):
        """
         Checking duplication product in move line within stock picking.
         """
        dupli = []
        no_dupli = [l.product_id.id for l in self.move_ids_without_package]
        for line in lines:
            if line[0] in [0, 1] and 'product_id' in line[2].keys():
                if line[2].get('product_id') not in no_dupli:
                    no_dupli.append(line[2].get('product_id'))
                else:
                    dupli.append(self.env['product.product'].browse(line[2].get('product_id')))

        dupli_set = set(dupli)
        if dupli_set:
            raise UserError(_("There are duplicate product with same barcode:\n%s") % (
                "\n".join(["%s[%s]" % (p.name, p.barcode) for p in dupli_set])))

    def button_validate(self):

        if self.picking_type_id.code == 'internal':
            res = True
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            # no_quantities_done = all(
            #     float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
            #     self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))

            # if no_quantities_done:
            #     raise UserError(_("Please set quantity."))

            if self.state in ['confirmed'] and self.inter_transfer_type in ['send', 'request']:
                raise UserError(_("Should checking quantity by source location user first."))

                return res
            elif self.state in ['assigned'] and self.inter_transfer_type in ['send', 'request']:
                if self.env.user.id in self.location_dest_id.user_ids.ids:

                    # Set quantity if didn't by user.
                    # self._force_set_quantity()

                    res = super(accerps_internal_transfers, self).button_validate()

                    _message = _("<p>The transfer <a href='%s'>%s</a> has been receipted by %s successfully</p>")

                    _args = (self._generate_current_form_url(), self.name, self.location_dest_id.name)
                    self.send_notification_users(_message % _args,
                                                 [user.partner_id.id for user in self.location_id.user_ids])
                else:
                    raise UserError(_("Please, wait until confirmed by destination location user."))

                return res

        else:
            res = super(accerps_internal_transfers, self).button_validate()

        return res

    def send_notification_users(self, message, partner_ids):
        return self.env['mail.thread'].sudo().message_notify(body=message, partner_ids=partner_ids)

    @api.model
    def create(self, vals):
        """
           Deny duplicate product with same barcode
        """
        if vals.get('move_ids_without_package'):
            self.check_duplicate_product_move_line(vals['move_ids_without_package'])

        return super(accerps_internal_transfers, self).create(vals)

    def write(self, vals):
        """
           Deny duplicate product with same barcode
        """

        if vals.get('move_ids_without_package'):
            self.check_duplicate_product_move_line(vals['move_ids_without_package'])

        return super(accerps_internal_transfers, self).write(vals)

    def _generate_current_form_url(self):
        url = "/web#id=%s&action=%s&model=stock.picking&view_type=form&cids="
        action_id = self.env.ref('stock.action_picking_tree_all').id
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return base_url+url % (self.id, action_id)

class StockMove(models.Model):
    _inherit = 'stock.move'

    # loc_src_qty_hand = fields.Float('Src location Qty', default=0.0)
    # loc_dest_qty_hand = fields.Float('Dest location Qty', default=0.0)

    @api.depends('product_id', 'product_uom_qty', 'picking_id.location_id', 'picking_id.location_dest_id')
    def _compute_prod_availability(self):
        for move in self:
            move.loc_src_qty_hand = 0.0
            move.loc_dest_qty_hand = 0.0
            if move.product_id:
                #move.loc_src_qty_hand = move.product_id.with_context(location_id=move.location_id).qty_available
                #move.loc_dest_qty_hand = move.product_id.with_context(location_id=move.location_dest_id).qty_available
                move.loc_src_qty_hand = move._get_available_qty(move.product_id, move.picking_id.location_id)
                move.loc_dest_qty_hand = move._get_available_qty(move.product_id, move.picking_id.location_dest_id)

    loc_src_qty_hand = fields.Float('Src location Qty', compute='_compute_prod_availability', readonly=True,
                                    default=0.00)
    loc_dest_qty_hand = fields.Float('Dest location Qty', compute='_compute_prod_availability', readonly=True,
                                     default=0.00)

    def _get_available_qty(self, product_id, location_id):
        stock_quant_sudo = self.env['stock.quant'].sudo()
        return stock_quant_sudo._get_available_quantity(product_id, location_id)
