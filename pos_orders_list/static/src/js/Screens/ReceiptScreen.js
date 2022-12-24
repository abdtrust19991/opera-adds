odoo.define('pos_orders_list.ReceiptScreen', function(require) {
	"use strict";

	const OrderReceipt = require('point_of_sale.OrderReceipt');
	const Registries = require('point_of_sale.Registries');

	const ReceiptScreen = OrderReceipt => 
		class extends OrderReceipt {
			constructor() {
				super(...arguments);
			}
			
			get receiptBarcode(){
				var order = this.env.pos.get_order();
				$("#barcode_print").barcode(
					order.barcode, // Value barcode (dependent on the type of barcode)
					"code128" // type (string)
				);
			return true
			}
		
	};

	Registries.Component.extend(OrderReceipt, ReceiptScreen);

	return OrderReceipt;
});