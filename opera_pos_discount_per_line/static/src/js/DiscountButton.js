odoo.define('opera_pos_discount_per_line.AllDiscountButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class AllDiscountButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            var self = this;

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

            await this.showNumberPopup();
        }

        async showNumberPopup(){

            const { confirmed, payload } = await this.showPopup('NumberPopup',{
                title: this.env._t('Discount Percentage'),
            });

            if (confirmed) {
                const val = Math.round(Math.max(0,Math.min(100,parseFloat(payload))));
                if(this.env.pos.config.apply_discount_limit && this.env.pos.config.discount_limit < val){
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Error'),
                        body: this.env._t('Discount Limit Exceed'),
                    });
                    return;
                }
                await this.apply_discount(val);
            }

        }

        async apply_discount(pc) {
            var order = this.env.pos.get_order();
            var lines = order.get_orderlines();

            var i = 0;
            while ( i < lines.length ) {
                if( lines[i].get_quantity() > 0 )
                    lines[i].set_discount(pc);

                i++;
            }
        }
    }

    AllDiscountButton.template = 'AllDiscountButton';

    ProductScreen.addControlButton({
        component: AllDiscountButton,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(AllDiscountButton);

    return AllDiscountButton;
});
