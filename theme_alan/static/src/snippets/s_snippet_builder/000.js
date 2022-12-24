odoo.define('theme_alan.alan_snippet_builder', function (require) {
"use strict";

var publicWidget = require('web.public.widget');

publicWidget.registry.alan_snippet_builder = publicWidget.Widget.extend({
    selector: "#wrapwrap",
    'events':{
        'click .popup-youtube':'_openVideoPop'
    },
    _openVideoPop:function(ev){
        ev.preventDefault();
        $(ev.currentTarget).magnificPopup({
            disableOn: 700,
            type: 'iframe',
            mainClass: 'mfp-fade',
            removalDelay: 160,
            preloader: false,
            fixedContentPos: false
        });
    },
});
});