odoo.define('theme_alan.s_blog_slider',function(require){
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.latest_blog = publicWidget.Widget.extend({
    selector : '.web_blog_slider',
    disabledInEditableMode: false,
    start: function (editable_mode) {
        var self = this;
        if (self.editableMode){
            self.$target.empty().append('<div class="seaction-head"><h2>Blog Slider</h2></div>');
        }
        if (!self.editableMode) {
            var list_id=self.$target.attr('data-blog_list-id') || false;
            $.get('/blog/get_blog_content',{'blog_config_id':list_id}).then(function (data){
                if(data){
                    self.$target.empty().append(data);
                    self.$target.removeClass('hidden');
                    $('.tqt-blog-slide').owlCarousel({
                        items: 4,
                        navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
                        margin: 30,
                        lazyLoad:true,
                        dots: true,
                        nav: true,
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
                            1024: {
                                items: 3,
                            }
                        }
                    });
                }
            });
        }
    },
});
});
