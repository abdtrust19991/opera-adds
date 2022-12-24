odoo.define('theme_alan.fron_offer_timer',function(require) {
'use strict';

var sAnimation = require('website.content.snippets.animation');
var timer;

sAnimation.registry.offer_timer = sAnimation.Class.extend({
    selector : '.offer_timer',
    start: function() {
        var self = this;
        var date = self.$target.data('date');
        if(date != 'nan') {
            var inputDate = new Date(date).getTime();
            timer = setInterval(function() {
                var now = new Date().getTime();
                var distance = inputDate - now ;
                if (distance > 0) {
                    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    if ((seconds+'').length == 1) {
                        seconds = '0' + seconds;
                    }
                    if ((days+'').length == 1) {
                        days = '0' + days;
                    }
                    if ((hours+'').length == 1) {
                        hours = '0' + hours;
                    }
                    if ((minutes+'').length == 1) {
                        minutes = '0' + minutes;
                    }
                }
                if(distance > 0 && self.$target.find('.snippet_offer_timer')) {
                    self.$target.find('.snippet_offer_timer').remove()
                    var append_data="<div class='snippet_offer_timer'><ul contenteditable='false'><li><span>"+ days +"</span><label>Days</label></li><li><span>"+hours+"</span><label>Hours</label></li><li><span>"+minutes+"</span><label>Minutes</label></li><li><span>"+seconds+"</span><label>Seconds</label></li></ul></div>";
                    self.$target.find('.snippet_offer_timer').css('display','block')
                    self.$target.append(append_data)
                }
                else {
                    self.$target.find('.snippet_offer_timer').remove()
                    var append_data="<div class='snippet_offer_timer'><ul><li><span>"+ '00' +"</span><label>Days</label></li><li><span>"+ '00' +"</span><label>Hours</label></li><li><span>"+ '00' +"</span><label>Minutes</label></li><li><span>"+ '00' +"</span><label>Seconds</label></li></ul></div>";
                    self.$target.find('.snippet_offer_timer').css('display','block')
                    self.$target.append(append_data)
                }
            }, 1000);
        }
    },
});
});
