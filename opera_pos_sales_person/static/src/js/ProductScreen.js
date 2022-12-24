odoo.define('opera_pos_sales_person.ProductScreen', function(require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const ProductScreenExt = ProductScreen => class extends ProductScreen {

        _onClickPay() {
            
            const currentOrder = this.env.pos.get_order();
            if(!currentOrder.sale_person_id){
                this.showPopup('ErrorPopup', {
                      title: _('Sales Person is required!'),
                });
                return;
            }
            super._onClickPay();
        }
       
    }

    Registries.Component.extend(ProductScreen, ProductScreenExt);

    return ProductScreen;
});
