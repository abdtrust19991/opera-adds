odoo.define('opera_pos_order_return.PosReturnButton', function (require) {
    'use strict';

    const { useListener } = require('web.custom_hooks');
    const { useContext } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const OrderManagementScreen = require('point_of_sale.OrderManagementScreen');
    const Registries = require('point_of_sale.Registries');
    const contexts = require('point_of_sale.PosContext');

    class PosReturnButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this._onClick);
            this.orderManagementContext = useContext(contexts.orderManagement);
        }
        get selectedOrder() {
            return this.orderManagementContext.selectedOrder;
        }
        set selectedOrder(value) {
            this.orderManagementContext.selectedOrder = value;
        }

        async _onClick() {
            const order = this.orderManagementContext.selectedOrder;
            if (!order) return;

            this.showPopup('PosReturnOrderPopup', { order: order });

        }

    }
    PosReturnButton.template = 'PosReturnButton';

    OrderManagementScreen.addControlButton({
        component: PosReturnButton,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(PosReturnButton);

    return PosReturnButton;
});
