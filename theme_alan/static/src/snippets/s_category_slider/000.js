odoo.define('theme_alan.s_category_slider',function(require){
'use strict';

var ajax = require('web.ajax');
var sAnimation = require('website.content.snippets.animation');

sAnimation.registry.cat_slider_actions = sAnimation.Class.extend({
    selector: '.as_cat_slider',
    disabledInEditableMode: false,

    start: function (editable_mode) {
        var self = this;
        if (self.editableMode){
            self.$target.empty().append('<div class="container"><div class="seaction-head"><h2> '+ self.$target.attr('data-collection_name') +' </h2></div></div>');
        }
        if (!self.editableMode) {
            this.getCategoryData();
        }
    },
    getCategoryData: function(){
        var self = this;
        var list_id = self.$target.attr('data-collection_id') || false;
        ajax.jsonRpc('/shop/get_category_snippet_content', 'call', {
            'collection_id': list_id
        }).then(function(data) {
            if(!data.disable_group){
                self.$target.empty().append(data.slider);
                self.$target.find('#as_category_slider_1').owlCarousel({
                    items: 4,
                    margin: 10,
                    autoplay: false,
                    autoplaySpeed: 5000,
                    autoplayHoverPause: true,
                    dots: false,
                    nav: true,
                    lazyLoad:true,
                    navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
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
                            items: 4,
                        }
                    }
                });
                self.$target.find('#as_category_slider_3').owlCarousel({
                    items: 2,
                    center:true,
                    loop: true,
                    margin: 10,
                    autoplay: false,
                    autoplaySpeed: 5000,
                    autoplayHoverPause: true,
                    dots: false,
                    nav: true,
                    lazyLoad:true,
                    navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
                    responsive: {
                        0: {
                            items: 1,
                        },
                        481: {
                            items: 1,
                        },
                        768: {
                            items: 2,
                        }
                    }
                });
                self.$target.find('#as_category_slider_4').owlCarousel({
                    items: 2,
                    loop: true,
                    margin: 0,
                    autoplay: false,
                    autoplaySpeed: 5000,
                    autoplayHoverPause: true,
                    dots: false,
                    nav: true,
                    lazyLoad:true,
                    navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
                    responsive: {
                        0: {
                            items: 1,
                        },
                        481: {
                            items: 2,
                        },
                        768: {
                            items: 2,
                        },
                        992: {
                            items: 3,
                        },
                        1200: {
                            items: 4,
                        },
                        1300: {
                            items: 5,
                        }
                    }
                });
                self.$target.find('#as_category_slider_6').owlCarousel({
                    items: 2,
                    center:true,
                    loop: true,
                    margin: 0,
                    autoplay: false,
                    autoplaySpeed: 5000,
                    autoplayHoverPause: true,
                    dots: false,
                    nav: true,
                    lazyLoad:true,
                    navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
                    responsive: {
                        0: {
                            items: 2,
                        },
                        481: {
                            items: 2,
                        },
                        768: {
                            items: 3,
                        },
                        992: {
                            items: 4,
                        },
                        1200: {
                            items: 4,
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
