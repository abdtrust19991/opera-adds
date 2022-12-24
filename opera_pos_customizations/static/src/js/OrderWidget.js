odoo.define('opera_pos_customizations.OrderWidget', function(require) {
    'use strict';

    const OrderWidget = require('point_of_sale.OrderWidget');
    const Registries = require('point_of_sale.Registries');
    
    const OrderWidgetExtend = OrderWidget => class extends OrderWidget {

        _updateSummary() {
            const total_sale_qty = this.order ? this.order.get_total_sale_qty() : 0;
            const total_return_qty = this.order ? this.order.get_total_return_qty() : 0;
            this.state.total_sale_qty = total_sale_qty;
            this.state.total_return_qty = total_return_qty;
            super._updateSummary();
        }
    
    }
    
    Registries.Component.extend(OrderWidget , OrderWidgetExtend);

    return OrderWidget;

})