odoo.define('theme_alan.vertical_slider', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var VariantMixin = require('sale.VariantMixin');

VariantMixin._onChangeProductImage = function (ev) {
    $('.thumbnails-slides').slick({
        arrows:true,
        infinite: false,
        slidesToShow: 5,
        slidesToScroll: 1,
        verticalSwiping: true,
        vertical: true,
        nextArrow: '<button type="button" class="next vertical" id="thumb_nxt"><span class="fa fa-angle-down"/></button>',
        prevArrow: '<button type="button" class="prev vertical" id="thumb_pre"><span class="fa fa-angle-up"/></button>',
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