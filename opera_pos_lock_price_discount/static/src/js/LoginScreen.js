odoo.define('opera_pos_lock_price_discount.LoginScreen', function (require) {
    'use strict';

    const LoginScreen = require('pos_hr.LoginScreen');
    const Registries = require('point_of_sale.Registries');

    const LoginScreenExtend = LoginScreen => class extends LoginScreen {
    
        async closeSession() {
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
            this.trigger('close-pos');
        }
    }

    Registries.Component.extend(LoginScreen , LoginScreenExtend);

    return LoginScreen;


});
