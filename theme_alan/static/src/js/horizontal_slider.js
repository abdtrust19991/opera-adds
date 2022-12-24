odoo.define('theme_alan.horizontal_slider', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var VariantMixin = require('sale.VariantMixin');

VariantMixin._onChangeProductImage = function (ev) {
    function rtl_slick(){
        if ($('#wrapwrap').hasClass("o_rtl")) {
            return true;
        } else {
            return false;
        }
    }

    $('.thumbnails-slides').slick({
        dots: false,
        infinite: false,
        speed: 300,
        slidesToShow: 6,
        slidesToScroll: 1,
        rtl: rtl_slick(),
        centerPadding: '10px',
        nextArrow: '<button type="button" class="next" id="thumb_nxt"><span class="fa fa-angle-right"/></button>',
        prevArrow: '<button type="button" class="prev" id="thumb_pre"><span class="fa fa-angle-left"/></button>'
    });

};

publicWidget.registry.WebsiteSale.include({
    _updateProductImage: function ($productContainer, displayImage, productId, productTemplateId, newCarousel, isCombinationPossible) {
        this._super.apply(this, arguments);
        VariantMixin._onChangeProductImage.apply(this, arguments);
    }
});

return VariantMixin;

});
