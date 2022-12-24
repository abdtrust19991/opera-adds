odoo.define('opera_pos_lock_price_discount.OrderManagementButton', function (require) {
    'use strict';

    const OrderManagementButton = require('point_of_sale.OrderManagementButton');
    const Registries = require('point_of_sale.Registries');
    const { isRpcError } = require('point_of_sale.utils');

    const OrderManagementButtonExtend = OrderManagementButton => class extends OrderManagementButton {
        async onClick() {
            if (this.env.pos.config.lock_view_orders) {
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Orders Lock Password'),
                    body: this.env._t(
                        'Please Enter Orders Lock Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.view_orders_pwd ){
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Wrong Password'),
                            body: this.env._t('Wrong Password.'),
                        });
                        return;
                    }
                }
                else{
                    return;
                }
            }
            await super.onClick();
        }
    }

    Registries.Component.extend(OrderManagementButton , OrderManagementButtonExtend);

    return OrderManagementButton;
});
