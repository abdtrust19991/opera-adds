odoo.define('opera_pos_customizations.PaymentScreen', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');

    const PaymentScreenInherit = PaymentScreen => class extends PaymentScreen {

        addNewPaymentLine({ detail: paymentMethod }) {
            super.addNewPaymentLine(...arguments);
            $(document).find('[payment-data-id='+paymentMethod.id+']').hide();
        }
        deletePaymentLine(event) {
            const { cid } = event.detail;
            const line = this.paymentLines.find((line) => line.cid === cid);
            const payment_method_id = line.payment_method.id;
            super.deletePaymentLine(...arguments);
            $(document).find('[payment-data-id='+payment_method_id+']').show();
        }

    }

    Registries.Component.extend(PaymentScreen , PaymentScreenInherit);

    return PaymentScreen;
});
