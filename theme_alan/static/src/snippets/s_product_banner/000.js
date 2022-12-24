odoo.define('theme_alan.s_product_banner_slide_front', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.product_banner_slide_front = publicWidget.Widget.extend({
    'selector':'.as_product_banner_slider',
    disabledInEditableMode: false,
    start: function (editable_mode) {
        var self = this;
        if (self.editableMode){
            self.$target.empty().append('<div class="container"><div class="seaction-head"><h2>'+ self.$target.attr('data-sp_name')  +'</h2></div></div>');
        }
        if(!self.editableMode){
            var product_id=self.$target.attr('data-sp_id');
            if(product_id != '0'){
                var addCart = self.$target.attr('data-add_to_cart');
                var buyBtn = self.$target.attr('data-buy_btn');
                var prodRating = self.$target.attr('data-prod_rating');
                var prodLab = self.$target.attr('data-prob_label');
                var pos = self.$target.attr('data-pos');
                return self._rpc({
                    route: '/get/product_banner/',
                    params: {
                        'id':product_id,
                        'edit_mode':false,
                        'add_to_cart':addCart,
                        'buy_btn':buyBtn,
                        'prod_rating':prodRating,
                        'prod_label':prodLab,
                        'pos':pos,
                    }
                }).then(function (result) {
                    self.$target.empty().append(result['prods_banner_temp']);
                    self.initialize_owl()
                });
            }
        }
    },
    initialize_owl: function (autoplay=false, items=4, slider_timing=5000) {
        $('.prod_banner_carousel_list').owlCarousel({
            items:1,
            loop:true,
            margin:10,
            merge:true,
            responsive:{
                0: {
                    items: 1,
                },
                768: {
                    items: 1,
                }
            }
        });
    },
});
});
