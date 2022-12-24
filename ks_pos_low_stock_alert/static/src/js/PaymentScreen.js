odoo.define('ks_pos_low_stock_alert.PaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');

    var ks_utils = require('ks_pos_low_stock_alert.utils');

    const PaymentScreenSbs = PaymentScreen => class extends PaymentScreen {

        async validateOrder(isForceValidate) {
            if (await this._isOrderValid(isForceValidate) && ks_utils.ks_validate_order_items_availability(this.env.pos.get_order(), this.env.pos.config, Gui)) {
                // remove pending payments before finalizing the validation
                for (let line of this.paymentLines) {
                    if (!line.is_done()) this.currentOrder.remove_paymentline(line);
                }
                await this._finalizeValidation();
            }
        }

        async _postPushOrderResolve(order, order_server_ids) {
            try {
                this.env.pos.ks_update_product_qty_from_order(order);
            } finally {
                return super._postPushOrderResolve(order, order_server_ids);
            }
        }

    }

    Registries.Component.extend(PaymentScreen, PaymentScreenSbs);

    return PaymentScreen;
});
