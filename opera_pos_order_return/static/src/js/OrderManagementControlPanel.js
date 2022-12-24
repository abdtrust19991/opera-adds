odoo.define('opera_pos_order_return.OrderManagementControlPanel', function (require) {
    'use strict';

    const OrderManagementControlPanel = require('point_of_sale.OrderManagementControlPanel');
    const Registries = require('point_of_sale.Registries');

    const VALID_SEARCH_TAGS = new Set(['date', 'customer', 'client', 'name', 'order','barcode']);
    const FIELD_MAP = {
        date: 'date_order',
        customer: 'partner_id.display_name',
        client: 'partner_id.display_name',
        name: 'pos_reference',
        order: 'pos_reference',
        barcode: 'barcode',
    };
    const SEARCH_FIELDS = ['pos_reference', 'partner_id.display_name', 'date_order', 'barcode'];

    const OrderManagementControlPanelExtend = OrderManagementControlPanel => class extends OrderManagementControlPanel {

        get validSearchTags() {
            return VALID_SEARCH_TAGS;
        }
        get fieldMap() {
            return FIELD_MAP;
        }
        get searchFields() {
            return SEARCH_FIELDS;
        }

    }

    Registries.Component.extend(OrderManagementControlPanel , OrderManagementControlPanelExtend);

    return OrderManagementControlPanel;
});
