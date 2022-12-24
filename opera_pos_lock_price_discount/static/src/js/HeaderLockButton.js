odoo.define('opera_pos_lock_price_discount.HeaderLockButton', function(require) {
    'use strict';

    const HeaderLockButton = require('point_of_sale.HeaderLockButton');
    const Registries = require('point_of_sale.Registries');

    const HeaderLockButtonExtend = HeaderLockButton => class extends HeaderLockButton {
    
        async showLoginScreen() {
            if (this.env.pos.config.lock_change_cashier) {
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Change Cashier Lock Password'),
                    body: this.env._t(
                        'Please Enter Change Cashier Lock Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.change_cashier_pwd ){
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
            await super.showLoginScreen(...arguments);
        }

    }

    Registries.Component.extend(HeaderLockButton , HeaderLockButtonExtend);

    return HeaderLockButton;
});
