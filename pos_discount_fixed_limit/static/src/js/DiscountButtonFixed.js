odoo.define('pos_discount_fixed_limit.DiscountButtonFixed', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class DiscountButtonFixed extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            var self = this;
            var user = this.env.pos.user;
            const { confirmed, payload } = await this.showPopup('NumberPopup',{
                title: this.env._t('Cash Discount'),
                startingValue: this.env.pos.config.discount_fixed,
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
                await self.apply_discount_fixed(val);
            }
        }

        async apply_discount_fixed(pc) {
            var order    = this.env.pos.get_order();
            var lines    = order.get_orderlines();
            var product  = this.env.pos.db.get_product_by_id(this.env.pos.config.discount_product_id[0]);
            if (product === undefined) {
                await this.showPopup('ErrorPopup', {
                    title : this.env._t("No discount product found"),
                    body  : this.env._t("The discount product seems misconfigured. Make sure it is flagged as 'Can be Sold' and 'Available in Point of Sale'."),
                });
                return;
            }

            // Remove existing discounts
            var i = 0;
            while ( i < lines.length ) {
                if (lines[i].get_product() === product) {
                    order.remove_orderline(lines[i]);
                } else {
                    i++;
                }
            }

            // Add discount

            var discount = - pc;

            if( discount < 0 ){
                order.add_product(product, {
                    price: discount,
                    lst_price: discount,
                    extras: {
                        price_manually_set: true,
                    },
                });
            }
        }
    }
    DiscountButtonFixed.template = 'DiscountButtonFixed';

    ProductScreen.addControlButton({
        component: DiscountButtonFixed,
        condition: function() {
            return this.env.pos.config.module_pos_discount && this.env.pos.config.discount_product_id;
        },
    });

    Registries.Component.add(DiscountButtonFixed);

    return DiscountButtonFixed;
});
