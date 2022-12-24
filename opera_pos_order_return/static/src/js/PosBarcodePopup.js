odoo.define('opera_pos_order_return.PosBarcodePopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const OrderFetcher = require('point_of_sale.OrderFetcher');

    class PosBarcodePopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({ inputValue: this.props.startingValue });
            this.inputRef = useRef('input');

            OrderFetcher.setComponent(this);
            OrderFetcher.setConfigId(this.env.pos.config_id);
            OrderFetcher.setPage(1);
            OrderFetcher.setNPerPage(1);

        }
        mounted() {
            this.inputRef.el.focus();
        }
        getPayload() {
            return this.state.inputValue;
        }

        async confirm() {
            const barcode = await this.getPayload();
            var domain = [['barcode','=',barcode]]

            OrderFetcher.setSearchDomain(domain);
            OrderFetcher.setPage(1);
            await OrderFetcher.fetch();
            var orders = OrderFetcher.get();
            if(orders && orders.length === 1){
//                OrderManagementScreen.trigger('click-order', orders[0]);
//                OrderManagementScreen._onClickOrder({ detail: orders[0] })
                this.showScreen('OrderManagementScreen');
                this.trigger('close-popup');
//                $('div.item.name').click();
            }
            else{
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t(
                        'Invalid Order Barcode'
                    ),
                });
            }
        }
    }

    PosBarcodePopup.template = 'BarcodePopup';
    PosBarcodePopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',
        startingValue: '',
    };

    Registries.Component.add(PosBarcodePopup);

    return PosBarcodePopup;
});
