odoo.define('whatever.filter_button', function (require) {

"use strict";

var core = require('web.core');

var ListController = require('web.ListController');

    ListController.include({

        renderButtons: function($node) {

        this._super.apply(this, arguments);

            if (this.$buttons) {

                let filter_button = this.$buttons.find('.oe_filter_button');

                filter_button && filter_button.click(this.proxy('filter_button')) ;

            }

        },

        filter_button: function () {

            console.log('yay filter');
            this.do_action({
                    name :'Create Product Based On Category',
                   type: 'ir.actions.act_window',

                  res_model: 'create.product.wizard',

                 view_mode: 'form',

                 view_type: 'form',

                 views: [[false, 'form']],

                 target: 'new',

                 context:{}
});
console.log('DOnE filter');


            //implement your click logic here

        }

    });

})