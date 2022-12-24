odoo.define('opera_pos_lock_price_discount.SetPricelistButton', function(require) {
    'use strict';

    const SetPricelistButton = require('point_of_sale.SetPricelistButton');
    const Registries = require('point_of_sale.Registries');
    
    const LockSetPricelistButton = SetPricelistButton => class extends SetPricelistButton {

        async onClick() {
            if (this.env.pos.config.lock_pricselist) {
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Pricelist Lock Password'),
                    body: this.env._t(
                        'Please Enter Pricelist Lock Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.pricelist_pwd ){
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

    Registries.Component.extend(SetPricelistButton, LockSetPricelistButton);

    return SetPricelistButton;

})