# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

import json
import re
import logging
from odoo.exceptions import UserError

from urllib.parse import urljoin
from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
import requests

_logger = logging.getLogger(__name__)


class AcquirerHyperpay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('hyperpay1', 'Hyperpay Mada')], ondelete={'hyperpay1': 'set default'})
    hyperpay1_entity_id = fields.Char(string='Merchant ID/Entity Id', required_if_provider='hyperpay1',
                                      groups='base.group_user')
    hyperpay1_authorization_bearer = fields.Char(
        string='Authorization Bearer', required_if_provider='hyperpay1', groups='base.group_user')

    @api.model
    def _get_authorize_urls2(self, environment):
        """ Hyperpay URLS """
        if environment == 'prod':
            return {
                'hyperpay_form_url': 'https://oppwa.com/v1/checkouts',
            }
        else:
            return {
                'hyperpay_form_url': 'https://test.oppwa.com/v1/payments',
            }

    def _get_authenticate2(self, values):
        url = "https://test.oppwa.com/v1/checkouts"
        authorization_bearer = self.hyperpay1_authorization_bearer
        data = {
            'entityId': self.hyperpay1_entity_id,
            'amount': str(format(values['amount'], '.2f')),
            'currency': values['currency'] and values['currency'].name or '',
            'paymentType': 'DB',
            'merchantTransactionId': values.get('reference'),
            'customer.email': values['partner_email'],
            'customer.givenName': values['partner_name'],
            'customer.companyName': values['billing_partner_commercial_company_name'],
            'customer.phone': values['partner_phone'],
            'billing.street1': values['billing_partner_address'],
            'billing.city': values['billing_partner_city'],
            'billing.state': values['billing_partner_state'].name,
            'billing.country': values['billing_partner_country'].code,
            'billing.postcode': values['billing_partner_zip'],
            'customer.surname': values['partner_last_name']

        }
        try:
            headers = {'Authorization': authorization_bearer}
            response = requests.post(
                url,
                headers=headers,
                data=data
            )
            response = json.loads(response.text)
            return response.get('id')
        except Exception as e:
            raise UserError(_(e))

    def hyperpay1_form_generate_values(self, values):
        base_url = self.get_base_url()
        check_out_id = self._get_authenticate2(values)
        authorization_bearer = self.hyperpay1_authorization_bearer
        print("hyperpay2", authorization_bearer)
        hyperpay1_tx_values = dict(values)
        hyperpay1_tx_values.update({
            'entityId': self.hyperpay1_entity_id,
            'check_out_id': check_out_id,
            'Authorization': authorization_bearer,
            'amount': str(format(values['amount'], '.2f')),
            'currency': values['currency'] and values['currency'].name or '',
            'paymentBrand': 'VISA',
            'paymentType': 'DB',
            'merchantTransactionId': values.get('reference'),
            'shopperResultUrl': '%s' % urljoin(base_url, '/shop/hyperpay1/payment/'),
            'hyperpay_return': '%s' % urljoin(base_url, '/payment/hyperpay1/return'),
            'custom': json.dumps(
                {'return_url': '%s' % hyperpay1_tx_values.pop('return_url')}) if hyperpay1_tx_values.get(
                'return_url') else False,
        })
        return hyperpay1_tx_values

    def hyperpay1_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_authorize_urls(environment)['hyperpay_form_url']


class TxHyperpay(models.Model):
    _inherit = 'payment.transaction'

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _hyperpay1_form_get_tx_from_data(self, data):

        reference, txn_id = data.get('merchantTransactionId'), data.get('id')

        if not reference or not txn_id:
            error_msg = _('Hyperpay: received data with missing reference (%s) or (%s)') % (reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Hyperpay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _hyperpay1_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        if self.acquirer_reference and data.get('id') != self.acquirer_reference:
            invalid_parameters.append(('id', data.get('id'), self.acquirer_reference))
        return invalid_parameters

    def _hyperpay1_form_validate(self, data):
        status_code = data.get('result').get('code')
        success_regex_1 = re.compile(r'000\.000\.|000\.100\.1|000\.[36]').search(status_code)
        success_regex_2 = re.compile(r'000\.400\.0[^3]|000\.400\.100').search(status_code)
        pending_regex_1 = re.compile(r'000\.200').search(status_code)
        pending_regex_2 = re.compile(r'800\.400\.5|100\.400\.500').search(status_code)
        error_regex_1 = re.compile(r'000\.100\.2').search(status_code)
        if success_regex_1 or success_regex_2:
            success_message = data.get('result').get('description') or 'success'
            logger_msg = _('Hyperpay:' + success_message)
            _logger.info(logger_msg)
            self.write({
                'acquirer_reference': data.get('id'),
            })
            self._set_transaction_done()
            return True
        elif pending_regex_1 or pending_regex_2:
            pending_message = data.get('result').get('description') or 'pending'
            logger_msg = _('Hyperpay:' + pending_message)
            _logger.info(logger_msg)
            self.write({'acquirer_reference': data.get('id')})
            self._set_transaction_pending()
            return True
        elif error_regex_1:
            error_message = data.get('result').get('description') or 'error'
            error = _('Hyperpay:' + error_message)
            _logger.info(error)
            self.write({'state_message': error})
            self._set_transaction_cancel()
            return False
        else:
            cancel_message = data.get('result').get('description') or 'cancel'
            logger_msg = _('Hyperpay:' + cancel_message)
            _logger.info(logger_msg)
            self.write({'acquirer_reference': data.get('id')})
            self._set_transaction_cancel()
            return True
