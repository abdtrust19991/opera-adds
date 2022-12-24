odoo.define('pos_discount_limit.DiscountButton', function(require) {
    'use strict';

    const DiscountButton = require('pos_discount.DiscountButton');
    const Registries = require('point_of_sale.Registries');

    const POSDiscountButtonLimit = DiscountButton =>
        class extends DiscountButton {
            /**
             * @override
             * Restrict apply discount by discount limit POS setting.
             */
            async apply_discount(pc) {
                if (this.env.pos.config.discount_pc_limit < pc){
                    await this.showPopup('ErrorPopup', {
                        title : this.env._t("Exceeded discount limit"),
                        body  : _.str.sprintf(this.env._t("You have exceeded the specified discount limit %s%%."), this.env.pos.config.discount_pc_limit),
                    });
                    await super.apply_discount(this.env.pos.config.discount_pc_limit);
                }
                else if (pc){
                    await super.apply_discount(pc);
                }
            }
        };
        Registries.Component.extend(DiscountButton, POSDiscountButtonLimit);

    return DiscountButton;
});
