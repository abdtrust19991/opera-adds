odoo.define('opera_pos_lock_price_discount.DiscountButton', function(require) {
    'use strict';

    const DiscountButton = require('pos_discount.DiscountButton');
    const Registries = require('point_of_sale.Registries');

    const DiscountButtonExtend = DiscountButton => class extends DiscountButton {
    
        async onClick() {
            if (this.env.pos.config.lock_global_discount) {
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Global Discount Lock Password'),
                    body: this.env._t(
                        'Please Enter Global Discount Lock Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.global_discount_password ){
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
            await super.onClick(...arguments);
        }

    }

    Registries.Component.extend(DiscountButton , DiscountButtonExtend);

    return DiscountButton;
});
