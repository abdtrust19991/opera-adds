odoo.define('pos_discount_limitation.pos_discount_limitation', function (require) {

var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;

var pos_discount = require('pos_discount.pos_discount');

pos_discount.DiscountButton.include({

    button_click: function(){
        this._super();
        var self = this;
        this.gui.show_popup('number',{
            'title': _t('Discount Percentage'),
            'value': this.pos.config.discount_pc,
            'confirm': function(val) {
                val = Math.min(Math.max(parseFloat(val) || 0, 0),100);
                self.apply_discount(val);
            },
        });
    },

	apply_discount: function(pc) {
		this._super();
        var user = this.pos.get_cashier();
        var self = this;
        rpc.query({
            model: 'pos.config',
            method: 'check_user_group',
            args: [user, pc],
            })
            .then(function (result) {
                var msg = _.str.sprintf(_t("You are not allowed to give discount more than %s!"), result['disc_limit']);
                if (result['disc_limit']){
                    self.gui.show_popup('error', {
                        title : _t("Discount Limit Exceed"),
                        body  : msg,
                    });
                    return;
                }else{
                    var order    = self.pos.get_order();
                    var lines    = order.get_orderlines();
                    var product  = self.pos.db.get_product_by_id(self.pos.config.discount_product_id[0]);
                    if (product === undefined) {
                        self.gui.show_popup('error', {
                            title : _t("No discount product found"),
                            body  : _t("The discount product seems misconfigured. Make sure it is flagged as 'Can be Sold' and 'Available in Point of Sale'."),
                        });
                        return;
                    }

                    // Remove existing discounts
                    var i = 0;
                    while ( i < lines.length ) {
                        if (lines[i].get_product() === product) {
                            order.remove_orderline(lines[i]);
                        } else {
                            i++;
                        }
                    }

                    // Add discount
                    // We add the price as manually set to avoid recomputation when changing customer.
                    pc = Math.round(Math.max(0,Math.min(100,pc)));
                    var discount = - pc / 100.0 * order.get_total_with_tax();

                    if( discount < 0 ){
                        order.add_product(product, {
                            price: discount,
                            extras: {
                                price_manually_set: true,
                            },
                        });
                    }
                }
            });
        
    },
})

});