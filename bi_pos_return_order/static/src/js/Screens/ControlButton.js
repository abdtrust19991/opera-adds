odoo.define('bi_pos_return_order.ReturnOrderButton', function(require) {
	'use strict';

	const PosComponent = require('point_of_sale.PosComponent');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const { useListener } = require('web.custom_hooks');
	const Registries = require('point_of_sale.Registries');

	class ReturnOrderButton extends PosComponent {
		constructor() {
			super(...arguments);
			useListener('click', this.onClick);
		}
		async onClick() {
			let self = this;
			const { confirmed, payload: inputNote } = await this.showPopup('TextInputPopup', {
				title: this.env._t('Return Order Barcode'),
			});

			if (confirmed) {
				let entered_barcode = inputNote;
				let order = self.env.pos.db.get_orders_by_barcode[entered_barcode];
				if(order){
					let orderlines = [];
					$.each(order.lines, function(index, value) {
						let ol = self.env.pos.db.get_orderline_by_id[value];
						orderlines.push(ol);
					});
					self.showPopup('ReturnOrderPopup', {
						'order': order, 
						'orderlines':orderlines,
					});
				}else{
					self.showPopup('ErrorPopup', {
						'title': self.env._t('Invalid Barcode'),
						'body': self.env._t("No Order Found for this Barcode"),
					});
				}
			}
		}
	}
	ReturnOrderButton.template = 'ReturnOrderButton';

	ProductScreen.addControlButton({
		component: ReturnOrderButton,
		condition: function() {
			return this.env.pos.config.show_order;
		},
	});

	Registries.Component.add(ReturnOrderButton);

	return ReturnOrderButton;
});
