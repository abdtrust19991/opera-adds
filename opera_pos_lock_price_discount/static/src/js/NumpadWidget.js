odoo.define('opera_pos_lock_price_discount.NumpadWidget', function (require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');
    
    const NumpadWidgetExtend = NumpadWidget => class extends NumpadWidget {

        async changeMode(mode) {
            if(mode === 'price' && this.env.pos.config.lock_price ){
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Price Lock Password'),
                    body: this.env._t(
                        'Please Enter Price Lock Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.price_password ){
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

            if(mode === 'discount' && this.env.pos.config.lock_discount ){
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Discount Lock Password'),
                    body: this.env._t(
                        'Please Enter Discount Lock Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.discount_password ){
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
            return super.changeMode(...arguments);
        }

        async onclickBackspace(){
            if (this.env.pos.config.lock_delete) {
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Backspace Lock Password'),
                    body: this.env._t(
                        'Please Enter Backspace Lock Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.delete_password ){
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
            super.sendInput('Backspace');
        }

        async onclickMinus(){
            if (this.env.pos.config.lock_change_sign) {
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Change Sign Lock Password'),
                    body: this.env._t(
                        'Please Enter Change Sign Lock Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.change_sign_pwd ){
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
            super.sendInput('-');
        }


    }

    Registries.Component.extend(NumpadWidget , NumpadWidgetExtend);

    return NumpadWidget;
    
})