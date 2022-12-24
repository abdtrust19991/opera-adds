odoo.define('bi_pos_reorder.POSOrdersScreen', function (require) {
	'use strict';

	const POSOrdersScreen = require('pos_orders_list.POSOrdersScreen');
	const Registries = require('point_of_sale.Registries');
	const {useState} = owl.hooks;
	const {useListener} = require('web.custom_hooks');

	const ReturnPOSOrdersScreen = (POSOrdersScreen) =>
		class extends POSOrdersScreen {
			constructor() {
				super(...arguments);
				useListener('click-returnOrder', this.clickReturnOrder);
			}
			
			clickReturnOrder(event){
				let self = this;
				let order = event.detail;
				let o_id = parseInt(event.detail.id);
				let orderlines =  self.orderlines;				
				let pos_lines = [];

				for(let n=0; n < orderlines.length; n++){
					if (orderlines[n]['order_id'][0] ==o_id){
						pos_lines.push(orderlines[n])
					}
				}
				self.showPopup('ReturnOrderPopup', {
					'order': event.detail, 
					'orderlines':pos_lines,
				});
			}
		}
		
	Registries.Component.extend(POSOrdersScreen, ReturnPOSOrdersScreen);

	return POSOrdersScreen;
});


