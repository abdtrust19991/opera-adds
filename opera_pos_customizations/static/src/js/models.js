odoo.define("opera_pos_customizations.models", function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');

    models.load_fields('product.product', 'type');

    var existing_models = models.PosModel.prototype.models;
    var partner_index = _.findIndex(existing_models, function (model) {
        return model.model === "res.partner";
    });
    var partner_model = existing_models[partner_index];
    partner_model.domain =  function(self){
            var domain = [['is_pos_customer','=',true]];

            return domain;
        }

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        prepare_new_partners_domain: function(){
            return [['write_date','>', this.db.get_partner_write_date()],['is_pos_customer','=', true]];
        },
    })

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

        get_total_sale_qty: function(){
            var total_qty = 0;
            var lines = this.get_orderlines();
            _.each(lines, function (line) {
                var qty = line.get_quantity();
                var product = line.get_product();
                if( product.type === 'product' && qty > 0 ){
                    total_qty += qty;
                }
            })
            return total_qty;
        },
        get_global_discount: function(){
            var discount = 0;
            var lines = this.get_orderlines();
            var discount_product_id = this.pos.config.discount_product_id;
            if( discount_product_id )
            {
                _.each(lines, function (line) {
                    var product = line.get_product();
                    if( product.id === discount_product_id[0] ){
                        discount += Math.abs(line.get_unit_price() );
                    }
                })
            }
            return discount;
        },
        get_total_return_qty: function(){
            var total_qty = 0;
            var lines = this.get_orderlines();
            _.each(lines, function (line) {
                var qty = line.get_quantity();
                var product = line.get_product();
                if( product.type === 'product' && qty < 0 ){
                    total_qty += qty;
                }
            })
            return Math.abs(total_qty);
        },

    })

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        get_all_discount: function(){
            var lst_price = this.get_lst_price();
            if(lst_price){
                var unit_price = this.get_unit_price();
                var discounted_unit_price = unit_price * (1 - this.get_discount() /100.0 )
                return Math.round( ( 10000.0  * (lst_price - discounted_unit_price )  ) /lst_price ) / 100.0
            }else{
                return 0;
            }

        }
    })

});