odoo.define('theme_alan.faq', function(require) {
'use strict';

var ajax = require('web.ajax');
var publicWidget = require('web.public.widget');

publicWidget.registry.as_faq_slider = publicWidget.Widget.extend({
    selector: '.as_faq_slider',
    disabledInEditableMode: false,
    start: function (editable_mode) {
        var self = this;
        if (self.editableMode){
            self.$target.empty();
        }
        if (!self.editableMode) {
            self.getWebsiteFaqData();
        }
    },
    getWebsiteFaqData: function(){
        if($('#wrapwrap .as_faq_slider').length){
            ajax.jsonRpc('/get_website_faq_list', 'call').then(function(data) {
                if (data) {
                    var content = $(data).find('.as_faq_slider');
                    $('.as_faq_slider').replaceWith(content);
                    $('.as_faq_slider').show();
                }
            });
        }
    },
});
});
