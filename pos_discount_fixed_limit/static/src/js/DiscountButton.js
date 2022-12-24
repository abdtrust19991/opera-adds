odoo.define('pos_discount_fixed_limit.DiscountButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const DiscountButton = require('pos_discount.DiscountButton');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;

    const TestDiscountButton = DiscountButton =>
        class extends DiscountButton {
            async onClick() {
                var self = this;
                var user = this.env.pos.user;
                const { confirmed, payload } = await this.showPopup('NumberPopup',{
                    title: this.env._t('Discount Percentage'),
                    startingValue: this.env.pos.config.discount_pc,
                });
                if (confirmed) {
                    const val = Math.round(Math.max(0,Math.min(100,parseFloat(payload))));
                    if (user.fixed_limit > 0){
                        if (val > user.fixed_limit){
                            await this.showPopup('ConfirmPopup',{
                                title: this.env._t('Discount Limit Exceeded'),
                                body:  this.env._t('Given discount is more than the allowed discount. Maximum allowed discount is '+ user.fixed_limit+'.'),
                            });
                            return;
                        }
                    }
                    await self.apply_discount(val);
                }
            }
    };

    Registries.Component.extend(DiscountButton, TestDiscountButton);

    return DiscountButton;


});
