odoo.define('theme_alan.product_share', function (require) {
'use strict';

const publicWidget = require('web.public.widget');

publicWidget.registry.websiteBlog = publicWidget.Widget.extend({
    selector: '.product_share',
    events: {
        'click .o_pinterest, .o_twitter, .o_facebook, .o_linkedin , .o_mail': '_onShareProduct',
    },
    _onShareProduct: function (ev) {
        ev.preventDefault();
        var url = '';
        var $element = $(ev.currentTarget);
        var product_name = encodeURIComponent($('#product_name').html() || '');
        var product_desc = encodeURIComponent($('#product_desc').html() || '');
        var productURL = encodeURIComponent(window.location.href);
        var simpleProductURL = window.location.href;

        if ($element.hasClass('o_twitter')) {
            url = 'https://twitter.com/intent/tweet?tw_p=tweetbutton&text=Amazing Product : ' + product_name + ' ,' + product_desc + '! '+ productURL;
        } else if ($element.hasClass('o_facebook')) {
            url = 'https://www.facebook.com/sharer/sharer.php?u=' + productURL;
        } else if ($element.hasClass('o_linkedin')) {
            url = 'https://www.linkedin.com/sharing/share-offsite/?url=' + productURL;
        }else if ($element.hasClass('o_pinterest')) {
            url = 'http://pinterest.com/pin/create/button/?url='+ productURL +'&description='+ product_desc;
        }
        else if ($element.hasClass('o_mail')) {
            url = 'mailto:?subject=Check Amazing Product&amp;body=Check out this site' + simpleProductURL;
        }
        window.open(url, '', 'menubar=no, width=500, height=400');
    },
});
});
