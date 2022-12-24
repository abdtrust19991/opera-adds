/*
    @Author: SBS
*/

odoo.define('ks_pos_low_stock_alert.models', function (require) {
    "use strict";

    var ks_models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    ks_models.load_fields('product.product', ['type']);
    var ks_super_pos = ks_models.PosModel.prototype;

    ks_models.PosModel = ks_models.PosModel.extend({
        initialize: function (session, attributes) {
            this.ks_load_product_quantity_after_product();
            this.location_id = false;
            ks_super_pos.initialize.call(this, session, attributes);
        },

        ks_get_model_reference: function (ks_model_name) {
            var ks_model_index = this.models.map(function (e) {
                return e.model;
            }).indexOf(ks_model_name);
            if (ks_model_index > -1) {
                return this.models[ks_model_index];
            }
            return false;
        },

        ks_load_product_quantity_after_product: async function () {
            var ks_product_model = this.ks_get_model_reference('product.product');
            var ks_product_super_loaded = ks_product_model.loaded;
            ks_product_model.loaded = async (self, ks_products) => {
                var done = $.Deferred();
                var ids = ks_products.map(v=>v.id);

                // Update quantity per location.
                var loc_id = await self.sbs_get_current_location(self);
                var qty_products = await rpc.query({
                    model: 'stock.quant',
                    method: 'get_available_quantity',
                    args: [ids, loc_id],
                    }).then(function (qty_products){

                        return qty_products;
                    });

                for(var i = 0; i < ks_products.length; i++){

                    if(ks_products[i].type == 'product'){
                        top_loop:for(var j = 0; j < qty_products.length; j++){
                            if(ks_products[i].id == qty_products[j].id)
                                ks_products[i].qty_available = qty_products[j].qty;
                                continue top_loop;
                            }
                    }
                }

                if(!self.config.allow_order_when_product_out_of_stock){
                    var ks_blocked_product_ids = [];
                    for(var i = 0; i < ks_products.length; i++){
                        if(ks_products[i].qty_available <= 0 && ks_products[i].type == 'product'){
                            ks_blocked_product_ids.push(ks_products[i].id);
                        }
                    }
                    var ks_blocked_products = ks_products.filter(function(p, index, arr) {
                        return ks_blocked_product_ids.includes(p.id);
                    });
                    ks_products = ks_products.concat(ks_blocked_products);
                }

                ks_product_super_loaded(self, ks_products);
                self.ks_update_qty_by_product_id(self, ks_products);
                done.resolve();
            }
        },

        ks_update_qty_by_product_id(self, ks_products){

            if(!this.db.qty_by_product_id){
                this.db.qty_by_product_id = {};
            }
            ks_products.forEach(ks_product => {
                this.db.qty_by_product_id[ks_product.id] = ks_product.qty_available;
            });
            this.ks_update_qty_on_product();
        },

        ks_update_qty_on_product: function () {
            var self = this;
            var ks_products = self.db.product_by_id;
            var ks_product_quants = self.db.qty_by_product_id;
            for(var pro_id in self.db.qty_by_product_id){
                ks_products[pro_id].qty_available = ks_product_quants[pro_id];
            }
        },

        push_orders: function(ks_order, opts){
            var self = this;
            var ks_pushed = ks_super_pos.push_orders.call(this, ks_order, opts);

            if (ks_order){
                this.ks_update_product_qty_from_order(ks_order);
            }
            return ks_pushed;
        },

        push_and_invoice_order:function(ks_order){
            var self = this;
            var ks_pushed = ks_super_pos.push_and_invoice_order.call(this, ks_order);

            if (ks_order){
                this.ks_update_product_qty_from_order(ks_order);
            }

            return ks_pushed;
        },

        push_single_order:function(ks_order){
            var self = this;
            var ks_pushed = ks_super_pos.push_single_order.call(this, ks_order);
            if (ks_order){
                this.ks_update_product_qty_from_order(ks_order);
            }

            return ks_pushed;
        },

        ks_update_product_qty_from_order: function(ks_order){
            var self = this;
             ks_order.orderlines.forEach(line => {
                var ks_product = line.get_product();
                if(ks_product.type == 'product'){
                    ks_product.qty_available -= line.get_quantity();
                    self.ks_update_qty_by_product_id(self, [ks_product]);
                }
            });
        },
        sbs_get_current_location: async function (self) {
            var loc = await rpc.query({
                    model: 'stock.picking.type',
                    method: 'search_read',
                    args: [[['id', '=', self.config.picking_type_id[0]]], ['default_location_src_id']],
                })
                return loc.length>0 && loc[0].default_location_src_id[0];
        },
    });
       });