odoo.define('atharva_theme_base.pwa_config_js', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.pwa = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    start: function() {
        this._super.apply(this, arguments);
        this._rpc({
            route: '/pwa/is_active',
            params: {}
        }).then(function (result) {
            if(result == true){
                if('serviceWorker' in navigator){
                    navigator.serviceWorker.register('/service-worker-js')
                }
            }
            else{
                if(navigator.serviceWorker) {
                    navigator.serviceWorker.getRegistrations().then(function(reg) {
                        _.each(reg, function(sw) {
                            sw.unregister();
                        });
                    });
                }
            }
        });
    },
});
});