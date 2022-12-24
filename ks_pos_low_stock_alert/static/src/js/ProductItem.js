odoo.define('ks_pos_low_stock_alert.ProductItem', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const ProductItem = require('point_of_sale.ProductItem');

    const ProductItemSbs = ProductItem => class extends ProductItem {
        spaceClickProduct(event) {
            var is_out_stock = this.props.product.type == 'product' && (this.env.pos.config.allow_order_when_product_out_of_stock == false) && this.props.product.qty_available <= 0
            if (!is_out_stock)
            {
                super.spaceClickProduct(event);
            }
        }
    }

    Registries.Component.extend(ProductItem, ProductItemSbs);

    return ProductItem;
});