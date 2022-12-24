# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

import json
import logging
import pprint

import requests
import werkzeug
from werkzeug import urls

from odoo import http, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request
from odoo.exceptions import UserError, Warning

_logger = logging.getLogger(__name__)


class HyperpayController(http.Controller):

    @http.route('/payment/hyperpay1/return', type='http', auth='public', csrf=False)
    def hyperpay1_return(self, **post):
        """ Hyperpay."""
        acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', 'hyperpay1')], limit=1)
        if post.get('resourcePath'):
            url = "https://test.oppwa.com"
            url += post.get('resourcePath')
            url += '?entityId=' + acquirer.hyperpay1_entity_id
            authorization_bearer = acquirer.hyperpay1_authorization_bearer
            try:
                headers = {'Authorization': authorization_bearer}

                response = requests.get(
                    url,
                    headers=headers,
                )
                response = json.loads(response.text)
            except Exception as e:
                raise UserError(_(e))
            _logger.info(
                'Hyperpay: entering form_feedback with post data %s', pprint.pformat(post))
            request.env['payment.transaction'].sudo().form_feedback(response, 'hyperpay1')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/shop/hyperpay1/payment/', type='http', auth="none", csrf=False)
    def _payment_hyperpay1_card(self, **kw):
        return request.render("payment_hyperpay_mada.payment_hyperpay1_card",
                              {'check_out_id': kw.get('check_out_id'), 'return_url': kw.get('hyperpay_return')})
