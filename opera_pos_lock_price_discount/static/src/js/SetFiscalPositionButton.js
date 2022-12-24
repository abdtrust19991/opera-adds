odoo.define('pos_lock_price_discount.SetFiscalPositionButton', function(require) {
    'use strict';

    const SetFiscalPositionButton = require('point_of_sale.SetFiscalPositionButton');
    const Registries = require('point_of_sale.Registries');

    const LockSetFiscalPositionButton = SetFiscalPositionButton => class extends SetFiscalPositionButton {

        async onClick() {
            if (this.env.pos.config.lock_fiscal_position) {
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Fiscal Position Lock Password'),
                    body: this.env._t(
                        'Please Enter Fiscal Position Lock Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.fiscal_position_password ){
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

    Registries.Component.extend(SetFiscalPositionButton, LockSetFiscalPositionButton);

    return SetFiscalPositionButton;

});
