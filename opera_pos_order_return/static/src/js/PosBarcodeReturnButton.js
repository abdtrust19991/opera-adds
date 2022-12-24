odoo.define('opera_pos_order_return.PosBarcodeReturnButton', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    class PosBarcodeReturnButton extends PosComponent {

        async onClick() {
            if (this.env.pos.config.allow_return_password) {
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Barcode Return Password'),
                    body: this.env._t(
                        'Please Enter Barcode Return Password Password'
                    ),
                })
                if(confirmed){
                    if(payload !== this.env.pos.config.return_order_password ){
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

            await this.showPopup('PosBarcodePopup');
        }

    }
    PosBarcodeReturnButton.template = 'BarcodeReturnButton';

    ProductScreen.addControlButton({
        component: PosBarcodeReturnButton,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(PosBarcodeReturnButton);

    return PosBarcodeReturnButton;
});
