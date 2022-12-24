odoo.define('ks_pos_low_stock_alert.ProductScreen', function(require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');

    var ks_utils = require('ks_pos_low_stock_alert.utils');

    const ProductScreenSbs = ProductScreen => class extends ProductScreen {

        _onClickPay() {
            var self = this;
            const order = this.env.pos.get_order();

            if(ks_utils.ks_validate_order_items_availability(order, self.env.pos.config, Gui)) {
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    return line.has_valid_product_lot();
                });
                if(!has_valid_product_lot){
                    Gui.showPopup('ConfirmPopup',{
                        title: this.comp.env._t('Empty Serial/Lot Number'),
                        body:  this.comp.env._t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            this.showScreen('PaymentScreen');
                        },
                    });
                }else{
                    super._onClickPay();
                }
            }else
            {
                return;
            }

        }

        // Skip add product to cart when has no qty available.
        async _clickProduct(event) {
            const product = event.detail;

            var is_out_stock = product.type == 'product' && (this.env.pos.config.allow_order_when_product_out_of_stock == false) && product.qty_available <= 0;
            if (!is_out_stock)
            {
                super._clickProduct(event);
            }
        }

    }

    Registries.Component.extend(ProductScreen, ProductScreenSbs);

    return ProductScreen;
});
