odoo.define('opera_pos_order_return.PosReturnOrderPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class PosReturnOrderPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            useBarcodeReader({
                product: this._barcodeProductAction,
            })
            this.changes = {};
        }

        _barcodeProductAction(code){
            const barcode_elems = this.el.querySelector('.barcode_td');
            var barcode_elem = $(barcode_elems).filter('[data_barcode=' + code.base_code + ']');
            var input_elem = barcode_elem.parent().find('input')
            if(input_elem.length == 1){
                this.updateReturnQty(input_elem[0],true);
            }
        }

        updateReturnQty(input_elem,increment){
            var qty = parseInt(input_elem.attributes.qty.value || 0);
            var entered_qty = parseInt(input_elem.value || 0);
            var return_qty = parseInt(input_elem.attributes.return_qty.value || 0);

            if(increment)
                entered_qty += 1;

            var remain_qty = qty - return_qty;
            var to_order = entered_qty;
            if( entered_qty > qty || entered_qty > remain_qty ){
                input_elem.value = remain_qty;
                to_order = remain_qty;
            }else{
                input_elem.value = entered_qty;
            }
            this.changes[parseInt(input_elem.attributes.line_id.value)] = to_order;
        }

        captureChange(event) {
            this.updateReturnQty(event.target,false);
        }

        async confirm() {
            var return_products = {};
            var self = this;
            if(this.changes){
                var new_order = this.env.pos.add_new_order();
                var order = this.props.order;
                var lines = order.get_orderlines();
                var discount_product_id = this.env.pos.config.discount_product_id
                if(discount_product_id){
                    var discount_product = this.env.pos.db.get_product_by_id(discount_product_id[0]);
                }
                _.each(lines, function(line){
                    var return_qty = self.changes[line.id] || 0;
                    var product = line.get_product();
                    if(return_qty && return_qty > 0){
                        new_order.add_product(product,{
                            price: line.get_unit_price(),
                            discount: line.get_discount(),
                            quantity: -1 * return_qty,
                            merge: false,
                            extras: {
                                price_manually_set: true,
                            },
                        })
                        var new_line = new_order.get_selected_orderline();
                        new_line.order_line_id = line.id;
                        line.return_qty += return_qty;
                    }

                })
                if(discount_product_id ){
                    _.each(lines, function(line){
                        var product = line.get_product();
                        if(discount_product.id === product.id){
                            var global_discount_amount = Math.abs(line.get_unit_price());
                            var total = order.get_total_with_tax() + global_discount_amount;
                            var discount_ratio = global_discount_amount / parseFloat(total);
                            var total_with_tax_amount = new_order.get_total_with_tax();
                            var discount_amount = discount_ratio * total_with_tax_amount;
                            new_order.add_product(product, {
                                price:  Math.abs(discount_amount),
                                quantity: 1,
                                merge: false,
                                extras: {
                                    price_manually_set: true,
                                },
                            });
                        }

                    })
                }

                new_order.set_client(order.get_client());
                var paymentlines = order.get_paymentlines();

                new_order.sale_person_id = order.sale_person_id;
                new_order.sale_person_code = order.sale_person_code;
                new_order.sale_person_name = order.sale_person_name;

                new_order.return_order_id = order.backendId;

//                if(paymentlines && paymentlines.length > 0){
//                    new_order.add_paymentline(paymentlines[0].payment_method);
//                }

                new_order.trigger('change', new_order);
                this.showScreen('ProductScreen');
                this.trigger('close-popup');
            }

        }
    }

    PosReturnOrderPopup.template = 'PosReturnOrderPopup';
    PosReturnOrderPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',
        startingValue: '',
    };

    Registries.Component.add(PosReturnOrderPopup);

    return PosReturnOrderPopup;
});
