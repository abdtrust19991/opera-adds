odoo.define('theme_alan.load_on_scroll', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var call = false;

publicWidget.registry.ajaxProductLoadAuto = publicWidget.Widget.extend({
    selector:'div#wrapwrap',
    events:{
        'scroll':'_autoLoadShopProduct'
    },
    _autoLoadShopProduct:function(){
        if($('#nxt').offset() != undefined){
            var gettop = $('#nxt').offset().top;
            var getheight = $('#nxt').outerHeight();
            var getwindowheight = $(window).height();
            var nxtbtnpos = gettop+getheight-getwindowheight;
            if (nxtbtnpos < 30){
                if(call != true){
                    $('#nxt').click();
                    call = true;
                }
            }else{
                call = false;
            }
        }
    }
});
});
