odoo.define('opera_pos_lock_price_discount.TicketScreen', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const TicketScreen = require('point_of_sale.TicketScreen');
    const { useListener } = require('web.custom_hooks');
    const { posbus } = require('point_of_sale.utils');

    const TicketScreenExtend = TicketScreen => class extends TicketScreen {

        async deleteOrder(order) {

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
            await super.deleteOrder(...arguments);
        }

    }

    Registries.Component.extend(TicketScreen , TicketScreenExtend);

    return TicketScreen;
});
