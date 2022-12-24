odoo.define('theme_alan.elevatezoom', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.WebsiteSale.include({
    _startZoom: function () {
        $('.zoomContainer').remove();
        var $image = $('#o-carousel-product .carousel-item.active .product_detail_img');
        $image.removeData('elevateZoom');
        $image.elevateZoom({
            constrainType: 'height',
            constrainSize: 274,
            zoomType: 'lens',
            containLensZoom: true,
            cursor: 'pointer',
        });
    }
});

publicWidget.registry.websiteImageZoom = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    events: {
        'slid.bs.carousel #o-carousel-product': '_onChangeSlide',
    },
    _onChangeSlide: function (ev) {
        ev.preventDefault();
        var sale = new publicWidget.registry.WebsiteSale();
        sale._startZoom();
    },
});

});
