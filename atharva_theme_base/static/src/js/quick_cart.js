odoo.define('quick_cart.quick_cart', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var wSaleUtils = require('website_sale.utils');
var random_index = 0;
var random_class_list = ['warning', 'primary', 'secondary'];

publicWidget.registry.quickCart = publicWidget.Widget.extend({
    'selector':'.oe_website_sale',
    events: {
        'click a.js_cart' : '_onAddToCart'
    },
    _onAddToCart:function(event){
        var $card = $(event.currentTarget).closest('.o_wsale_product_btn');
        this._rpc({
            route: '/shop/cart/update_json',
            params: {
                product_id: $card.find('input[data-product-id]').data('product-id'),
                add_qty: 1
            },
        }).then(function (data) {
            wSaleUtils.updateCartNavBar(data);
            if(!("cart_quantity" in data)){
                $(".my_cart_quantity").css("display","none")
            }
            var $navButton = $('header .o_wsale_my_cart').first();
            if (!$(event.currentTarget).hasClass('as-color')) {
                $(event.currentTarget).addClass('as-color');
            }
            if(data['warning']){
                if($('#wrapwrap > #cart_warning_content').length === 0)
                    $('#wrapwrap').append("<div id='cart_warning_content'></div>");
                $("#wrapwrap > #cart_warning_content").append("<div class='add_cart_warning alert alert-" + random_class_list[random_index % 3] + " alert-dismissible fade show'  role='alert'><p class='warning-msg'>" + data['warning'] + "</p><button class='close-btn' type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button></div>");
                random_index++;
            }else{
                wSaleUtils.animateClone($navButton, $(event.currentTarget).parents('.oe_product'), 25, 40);
            }

        });
    }});
});