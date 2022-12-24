odoo.define('theme_alan.s_brand_slider',function(require){
'use strict';

var sAnimation = require('website.content.snippets.animation');
var ajax = require('web.ajax');

sAnimation.registry.brand_slider_actions = sAnimation.Class.extend({
    selector: '.as_brand_slider',
    disabledInEditableMode: false,
    start: function (editable_mode) {
        var self = this;
        if (self.editableMode){
            self.$target.empty().append('<div class="container"><div class="seaction-head"><h2>' + self.$target.attr('data-collection_name') + '</h2></div></div>');
        }
        if (!self.editableMode) {
            this.getBrandData();
        }
    },
    getBrandData: function(){
        var self = this;
        var list_id = self.$target.attr('data-collection_id') || false;
        ajax.jsonRpc('/shop/get_brand_snippet_content', 'call', {
            'collection_id': list_id
        }).then(function(data) {
            if(!data.disable_group){
                var slider = data.slider
                var autoplay = data.auto_slider_value
                var items = data.item_count
                var slider_timing = data.slider_timing
                self.$target.empty().append(slider);
                self.$target.find('.as_our_brand').owlCarousel({
                    loop: true,
                    rewind: true,
                    margin: 10,
                    nav: true,
                    lazyLoad:true,
                    dots: false,
                    navText : ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
                    autoplay: autoplay,
                    autoplaySpeed: parseInt(slider_timing) || 5000,
                    autoplayTimeout: 3000,
                    autoplayHoverPause:true,
                    items: items,
                    responsive: {
                        0: {
                            items: 2,
                        },
                        481: {
                            items: 3,
                        },
                        768: {
                            items: 4,
                        },
                        1024: {
                            items: parseInt(items) || 4,
                        }
                    }
                });
            } else {
                self.$target.empty().append("<div class='alert alert-danger'> Record has been deleted or disable </div>");
            }
        });
    },
});
});
