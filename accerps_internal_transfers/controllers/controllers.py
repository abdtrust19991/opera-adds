# -*- coding: utf-8 -*-
# from odoo import http


# class AccerpsInternalTransfers(http.Controller):
#     @http.route('/accerps_internal_transfers/accerps_internal_transfers/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accerps_internal_transfers/accerps_internal_transfers/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accerps_internal_transfers.listing', {
#             'root': '/accerps_internal_transfers/accerps_internal_transfers',
#             'objects': http.request.env['accerps_internal_transfers.accerps_internal_transfers'].search([]),
#         })

#     @http.route('/accerps_internal_transfers/accerps_internal_transfers/objects/<model("accerps_internal_transfers.accerps_internal_transfers"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accerps_internal_transfers.object', {
#             'object': obj
#         })
