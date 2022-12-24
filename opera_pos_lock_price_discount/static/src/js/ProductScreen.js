odoo.define('opera_pos_lock_price_discount.NumberBuffer', function(require) {
    'use strict';

//    const PosComponent = require('point_of_sale.PosComponent');
//    const ProductScreen = require('point_of_sale.ProductScreen');
//    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const { parse } = require('web.field_utils');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { Gui } = require('point_of_sale.Gui');
//    const { useListener } = require('web.custom_hooks');
//    const Registries = require('point_of_sale.Registries');
//    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
//    const { useState } = owl.hooks;

    NumberBuffer._updateBuffer =  function (input) {
            console.log('in buffer');
            const isEmpty = val => {
                return val === '' || val === null;
            };
            if (input === undefined || input === null) return;
            let isFirstInput = isEmpty(this.state.buffer);
            if (input === this.decimalPoint) {
                if (isFirstInput) {
                    this.state.buffer = '0' + this.decimalPoint;
                } else if (!this.state.buffer.length || this.state.buffer === '-') {
                    this.state.buffer += '0' + this.decimalPoint;
                } else if (this.state.buffer.indexOf(this.decimalPoint) < 0) {
                    this.state.buffer = this.state.buffer + this.decimalPoint;
                }
            } else if (input === 'Delete') {
                if (this.isReset) {
                    this.state.buffer = '';
                    this.isReset = false;
                    return;
                }
                this.state.buffer = isEmpty(this.state.buffer) ? null : '';
            } else if (input === 'Backspace') {
                if (this.isReset) {
                    this.state.buffer = '';
                    this.isReset = false;
                    return;
                }
                const buffer = this.state.buffer;
                if (isEmpty(buffer)) {
                    this.state.buffer = null;
                } else {
                    const nCharToRemove = buffer[buffer.length - 1] === this.decimalPoint ? 2 : 1;
                    this.state.buffer = buffer.substring(0, buffer.length - nCharToRemove);
                }
            } else if (input === '+') {
//                if (this.state.buffer[0] === '-') {
//                    this.state.buffer = this.state.buffer.substring(1, this.state.buffer.length);
//                }
            } else if (input === '-') {
//                if (isFirstInput) {
//                    this.state.buffer = '-0';
//                } else if (this.state.buffer[0] === '-') {
//                    this.state.buffer = this.state.buffer.substring(1, this.state.buffer.length);
//                } else {
//                    this.state.buffer = '-' + this.state.buffer;
//                }
            } else if (input[0] === '+' && !isNaN(parseFloat(input))) {
                // when input is like '+10', '+50', etc
                const inputValue = parse.float(input.slice(1));
                const currentBufferValue = this.state.buffer ? parse.float(this.state.buffer) : 0;
                this.state.buffer = this.component.env.pos.formatFixed(
                    inputValue + currentBufferValue
                );
            } else if (!isNaN(parseInt(input, 10))) {
                if (isFirstInput) {
                    this.state.buffer = '' + input;
                } else if (this.state.buffer.length > 12) {
                    Gui.playSound('bell');
                } else {
                    this.state.buffer += input;
                }
            }
            if (this.state.buffer === '-') {
                this.state.buffer = '';
            }
            // once an input is accepted and updated the buffer,
            // the buffer should not be in reset state anymore.
            this.isReset = false;

            this.trigger('buffer-update', this.state.buffer);
        }


//    const ProductScreenExtend = ProductScreen => class extends ProductScreen {
//
//
//
//    }
//
//    Registries.Component.extend(ProductScreen , ProductScreenExtend);

//    class ProductScreen extends ControlButtonsMixin(PosComponent) {
//        constructor() {
//            super(...arguments);
//            useListener('update-selected-orderline', this._updateSelectedOrderline);
//            useListener('new-orderline-selected', this._newOrderlineSelected);
//            useListener('set-numpad-mode', this._setNumpadMode);
//            useListener('click-product', this._clickProduct);
//            useListener('click-customer', this._onClickCustomer);
//            useListener('click-pay', this._onClickPay);
//            useBarcodeReader({
//                product: this._barcodeProductAction,
//                weight: this._barcodeProductAction,
//                price: this._barcodeProductAction,
//                client: this._barcodeClientAction,
//                discount: this._barcodeDiscountAction,
//                error: this._barcodeErrorAction,
//            })
//            onChangeOrder(null, (newOrder) => newOrder && this.render());
//            NumberBuffer.use({
//                nonKeyboardInputEvent: 'numpad-click-input',
//                triggerAtInput: 'update-selected-orderline',
//                useWithBarcode: true,
//            });
//            let status = this.showCashBoxOpening()
//            this.state = useState({ cashControl: status, numpadMode: 'quantity' });
//            this.mobile_pane = this.props.mobile_pane || 'right';
//        }
//        mounted() {
//            this.env.pos.on('change:selectedClient', this.render, this);
//        }
//        willUnmount() {
//            this.env.pos.off('change:selectedClient', null, this);
//        }
//        /**
//         * To be overridden by modules that checks availability of
//         * connected scale.
//         * @see _onScaleNotAvailable
//         */
//        get isScaleAvailable() {
//            return true;
//        }
//        get client() {
//            return this.env.pos.get_client();
//        }
//        get currentOrder() {
//            return this.env.pos.get_order();
//        }
//        showCashBoxOpening() {
//            if(this.env.pos.config.cash_control && this.env.pos.pos_session.state == 'opening_control')
//                return true;
//            return false;
//        }
//        async _clickProduct(event) {
//            if (!this.currentOrder) {
//                this.env.pos.add_new_order();
//            }
//            const product = event.detail;
//            let price_extra = 0.0;
//            let draftPackLotLines, weight, description, packLotLinesToEdit;
//
//            if (this.env.pos.config.product_configurator && _.some(product.attribute_line_ids, (id) => id in this.env.pos.attributes_by_ptal_id)) {
//                let attributes = _.map(product.attribute_line_ids, (id) => this.env.pos.attributes_by_ptal_id[id])
//                                  .filter((attr) => attr !== undefined);
//                let { confirmed, payload } = await this.showPopup('ProductConfiguratorPopup', {
//                    product: product,
//                    attributes: attributes,
//                });
//
//                if (confirmed) {
//                    description = payload.selected_attributes.join(', ');
//                    price_extra += payload.price_extra;
//                } else {
//                    return;
//                }
//            }
//
//            // Gather lot information if required.
//            if (['serial', 'lot'].includes(product.tracking) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
//                const isAllowOnlyOneLot = product.isAllowOnlyOneLot();
//                if (isAllowOnlyOneLot) {
//                    packLotLinesToEdit = [];
//                } else {
//                    const orderline = this.currentOrder
//                        .get_orderlines()
//                        .filter(line => !line.get_discount())
//                        .find(line => line.product.id === product.id);
//                    if (orderline) {
//                        packLotLinesToEdit = orderline.getPackLotLinesToEdit();
//                    } else {
//                        packLotLinesToEdit = [];
//                    }
//                }
//                const { confirmed, payload } = await this.showPopup('EditListPopup', {
//                    title: this.env._t('Lot/Serial Number(s) Required'),
//                    isSingleItem: isAllowOnlyOneLot,
//                    array: packLotLinesToEdit,
//                });
//                if (confirmed) {
//                    // Segregate the old and new packlot lines
//                    const modifiedPackLotLines = Object.fromEntries(
//                        payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
//                    );
//                    const newPackLotLines = payload.newArray
//                        .filter(item => !item.id)
//                        .map(item => ({ lot_name: item.text }));
//
//                    draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
//                } else {
//                    // We don't proceed on adding product.
//                    return;
//                }
//            }
//
//            // Take the weight if necessary.
//            if (product.to_weight && this.env.pos.config.iface_electronic_scale) {
//                // Show the ScaleScreen to weigh the product.
//                if (this.isScaleAvailable) {
//                    const { confirmed, payload } = await this.showTempScreen('ScaleScreen', {
//                        product,
//                    });
//                    if (confirmed) {
//                        weight = payload.weight;
//                    } else {
//                        // do not add the product;
//                        return;
//                    }
//                } else {
//                    await this._onScaleNotAvailable();
//                }
//            }
//
//            // Add the product after having the extra information.
//            this.currentOrder.add_product(product, {
//                draftPackLotLines,
//                description: description,
//                price_extra: price_extra,
//                quantity: weight,
//            });
//
//            NumberBuffer.reset();
//        }
//        _setNumpadMode(event) {
//            const { mode } = event.detail;
//            NumberBuffer.capture();
//            NumberBuffer.reset();
//            this.state.numpadMode = mode;
//        }
//        async _updateSelectedOrderline(event) {
//            if(this.state.numpadMode === 'quantity' && this.env.pos.disallowLineQuantityChange()) {
//                let order = this.env.pos.get_order();
//                let selectedLine = order.get_selected_orderline();
//                let lastId = order.orderlines.last().cid;
//                let currentQuantity = this.env.pos.get_order().get_selected_orderline().get_quantity();
//
//                if(selectedLine.noDecrease) {
//                    this.showPopup('ErrorPopup', {
//                        title: this.env._t('Invalid action'),
//                        body: this.env._t('You are not allowed to change this quantity'),
//                    });
//                    return;
//                }
//                if(lastId != selectedLine.cid)
//                    this._showDecreaseQuantityPopup();
//                else if(currentQuantity < event.detail.buffer)
//                    this._setValue(event.detail.buffer);
//                else if(event.detail.buffer < currentQuantity)
//                    this._showDecreaseQuantityPopup();
//            } else {
//                let { buffer } = event.detail;
//                let val = buffer === null ? 'remove' : buffer;
//                this._setValue(val);
//            }
//        }
//        async _newOrderlineSelected() {
//            NumberBuffer.reset();
//        }
//        _setValue(val) {
//            if (this.currentOrder.get_selected_orderline()) {
//                if (this.state.numpadMode === 'quantity') {
//                    this.currentOrder.get_selected_orderline().set_quantity(val);
//                } else if (this.state.numpadMode === 'discount') {
//                    this.currentOrder.get_selected_orderline().set_discount(val);
//                } else if (this.state.numpadMode === 'price') {
//                    var selected_orderline = this.currentOrder.get_selected_orderline();
//                    selected_orderline.price_manually_set = true;
//                    selected_orderline.set_unit_price(val);
//                }
//                if (this.env.pos.config.iface_customer_facing_display) {
//                    this.env.pos.send_current_order_to_customer_facing_display();
//                }
//            }
//        }
//        _barcodeProductAction(code) {
//            // NOTE: scan_product call has side effect in pos if it returned true.
//            if (!this.env.pos.scan_product(code)) {
//                this._barcodeErrorAction(code);
//            }
//        }
//        _barcodeClientAction(code) {
//            const partner = this.env.pos.db.get_partner_by_barcode(code.code);
//            if (partner) {
//                if (this.currentOrder.get_client() !== partner) {
//                    this.currentOrder.set_client(partner);
//                    this.currentOrder.set_pricelist(
//                        _.findWhere(this.env.pos.pricelists, {
//                            id: partner.property_product_pricelist[0],
//                        }) || this.env.pos.default_pricelist
//                    );
//                }
//                return true;
//            }
//            this._barcodeErrorAction(code);
//            return false;
//        }
//        _barcodeDiscountAction(code) {
//            var last_orderline = this.currentOrder.get_last_orderline();
//            if (last_orderline) {
//                last_orderline.set_discount(code.value);
//            }
//        }
//        // IMPROVEMENT: The following two methods should be in PosScreenComponent?
//        // Why? Because once we start declaring barcode actions in different
//        // screens, these methods will also be declared over and over.
//        _barcodeErrorAction(code) {
//            this.showPopup('ErrorBarcodePopup', { code: this._codeRepr(code) });
//        }
//        _codeRepr(code) {
//            if (code.code.length > 32) {
//                return code.code.substring(0, 29) + '...';
//            } else {
//                return code.code;
//            }
//        }
//        /**
//         * override this method to perform procedure if the scale is not available.
//         * @see isScaleAvailable
//         */
//        async _onScaleNotAvailable() {}
//        async _showDecreaseQuantityPopup() {
//            const { confirmed, payload: inputNumber } = await this.showPopup('NumberPopup', {
//                startingValue: 0,
//                title: this.env._t('Set the new quantity'),
//            });
//            let newQuantity = inputNumber !== ""? inputNumber: null;
//            if (confirmed && newQuantity !== null) {
//                let order = this.env.pos.get_order();
//                let selectedLine = this.env.pos.get_order().get_selected_orderline();
//                let currentQuantity = selectedLine.get_quantity()
//                if(selectedLine.is_last_line() && currentQuantity === 1 && newQuantity < currentQuantity)
//                    selectedLine.set_quantity(newQuantity);
//                else if(newQuantity >= currentQuantity)
//                    selectedLine.set_quantity(newQuantity);
//                else {
//                    let newLine = selectedLine.clone();
//                    let decreasedQuantity = currentQuantity - newQuantity
//                    newLine.order = order;
//
//                    newLine.set_quantity( - decreasedQuantity, true);
//                    order.add_orderline(newLine);
//                }
//            }
//        }
//        async _onClickCustomer() {
//            // IMPROVEMENT: This code snippet is very similar to selectClient of PaymentScreen.
//            const currentClient = this.currentOrder.get_client();
//            const { confirmed, payload: newClient } = await this.showTempScreen(
//                'ClientListScreen',
//                { client: currentClient }
//            );
//            if (confirmed) {
//                this.currentOrder.set_client(newClient);
//                this.currentOrder.updatePricelist(newClient);
//            }
//        }
//        _onClickPay() {
//            this.showScreen('PaymentScreen');
//        }
//        switchPane() {
//            if (this.mobile_pane === "left") {
//                this.mobile_pane = "right";
//                this.render();
//            }
//            else {
//                this.mobile_pane = "left";
//                this.render();
//            }
//        }
//    }
//    ProductScreen.template = 'ProductScreen';
//
//    Registries.Component.add(ProductScreen);

//    return ProductScreen;
});
