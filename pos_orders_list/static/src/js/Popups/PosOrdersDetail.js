odoo.define('pos_orders_list.PosOrdersDetail', function(require) {
	'use strict';

	const { useExternalListener } = owl.hooks;
	const PosComponent = require('point_of_sale.PosComponent');
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;

	class PosOrdersDetail extends AbstractAwaitablePopup {
		go_back_screen() {
			this.showScreen('ProductScreen');
			this.trigger('close-popup');
		}
	}
	
	PosOrdersDetail.template = 'PosOrdersDetail';
	Registries.Component.add(PosOrdersDetail);
	return PosOrdersDetail;
});
