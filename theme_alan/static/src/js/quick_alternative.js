odoo.define('theme_alan.quick_alternative_view', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.quick_altern = publicWidget.Widget.extend({
    'selector':'#wrapwrap',
    'events':{
        'click a.o_alter_view':'_getAlternativeProduct'
    },
    _getAlternativeProduct:function(ev){
        var prod_temp_id = $(ev.currentTarget).attr('data-product_template_id');
        return this._rpc({
            route: '/json/alternative_product/',
            params: {
                'prod_tmp_id':prod_temp_id,
            }
        }).then(function (result) {
            var $mini_popup_temp = $('html').find('.cart_lines_popup');
            if($mini_popup_temp.length == 0){
                $('html').find('header').append('<div class="cart_lines_popup"/>');
            }
            var $mini_popup_temp = $('html').find('.cart_lines_popup');
            $mini_popup_temp.empty().append(result['quickAlterTemp'].trim()).addClass('show_mini_cart');
            $('body').addClass('cart-open-on-body');
        });
    }
});
});
