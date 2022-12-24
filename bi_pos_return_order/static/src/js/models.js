// bi_pos_return_order js
odoo.define('bi_pos_return_order.models', function(require) {
	"use strict";

	var models = require('point_of_sale.models');

	var posorder_super = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attr, options) {
			this.return_order_ref = this.return_order_ref || false;
			posorder_super.initialize.call(this,attr,options);
		},

		set_return_order_ref: function (return_order_ref) {
			this.return_order_ref = return_order_ref;
		},

		export_as_JSON: function() {
			var json = posorder_super.export_as_JSON.apply(this,arguments);
			json.return_order_ref = this.return_order_ref  || false;
			return json;
		},

		init_from_JSON: function(json){
			posorder_super.init_from_JSON.apply(this,arguments);
			this.return_order_ref = json.return_order_ref || false;
		},

	});


	var OrderlineSuper = models.Orderline.prototype;
	models.Orderline = models.Orderline.extend({

		initialize: function(attr, options) {
			this.original_line_id = this.original_line_id || false;
			OrderlineSuper.initialize.call(this,attr,options);
		},

		set_original_line_id: function(original_line_id){
			this.original_line_id = original_line_id;
		},

		get_original_line_id: function(){
			return this.original_line_id;
		},

		export_as_JSON: function() {
			var json = OrderlineSuper.export_as_JSON.apply(this,arguments);
			json.original_line_id = this.original_line_id || false;
			return json;
		},
		
		init_from_JSON: function(json){
			OrderlineSuper.init_from_JSON.apply(this,arguments);
			this.original_line_id = json.original_line_id;
		},

	});

});