odoo.define('opera_pos_receipt.custom', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var field_utils = require('web.field_utils');

    models.load_fields('pos.order', ['sale_person_id']);
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_for_printing: function () {
            var result = _super_order.export_for_printing.apply(this, arguments);
//            const order = this.pos.get_order();
            var total_sale_qty = this.get_total_sale_qty()
            var total_return_qty = this.get_total_return_qty()
            var shop = this.pos.config.name
            var barcode = this.barcode
            var sale_person = this.sale_person_name
            var sale_person_code = this.sale_person_code
            var global_discount = this.get_global_discount();
            var all_discount = global_discount + result.total_discount;

            result.total_sale_qty = total_sale_qty
            result.total_return_qty = total_return_qty
            result.shop = shop
            result.barcode = barcode
            result.global_discount = global_discount
            result.all_discount = all_discount

            result.sale_person = sale_person
            result.sale_person_code = sale_person_code
            result.date.localestring = field_utils.format.datetime(moment(this.validation_date), {}, {timezone: false});
            return result;
        },
    });

});