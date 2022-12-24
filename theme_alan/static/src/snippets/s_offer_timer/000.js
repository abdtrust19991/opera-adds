odoo.define('theme_alan.s_offer_timer',function(require){
'use strict';

var publicWidget = require('web.public.widget');
var timer;

publicWidget.registry.WebsiteSale.include({
    _onChangeCombination: function (ev, $parent, combination){
        this._super.apply(this, arguments);
        var self = this;
        var product_offer;
        clearInterval(timer);
        var start_date = new Date(combination.start_date)
        var current_date = new Date(combination.current_date)
        var end_date = new Date(combination.end_date)
        var msg = combination.deals_msg
        if(msg){
            $('.timer_msg').empty()
            var append_msg ="<div><span class='text-black'>"+msg+"</span></div>"
            $('.timer_msg').append(append_msg)
        }
        else {
            $('.timer_msg').empty()
        }
        if(start_date != 'nan'){
            timer = setInterval(function() {
                var now = new Date();
                if (start_date <= current_date && end_date >= current_date) {
                    var duration = end_date - now;
                    var distance = duration + 86400000
                    product_offer = true;
                } else {
                    product_offer = false;
                }
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
                if(product_offer == true && distance > 0) {
                    self.$target.find('.right_timer_div').remove();
                    var append_data="<div class='right_timer_div text-left mt16 date_time'>\
                    <span class='col-lg-3 col-md-3 col-sm-3 col-3 text-center d-inline-block p-0 pr-4'>\
                    <div class='rounded_digit py-3'><span id='days' class='d-block  te_days_hr_min_sec_digit text-black'>"+  days +"</span><span id='d_lbl' class='d-block'>Days</span></div></span><span class='col-lg-3 col-md-3 col-sm-3 col-3 text-center d-inline-block p-0 pr-4'><div class='rounded_digit py-3'><span id='hours' class='d-block  te_days_hr_min_sec_digit text-black'>"+hours+"</span><span id='h_lbl' class='d-block'>Hrs</span></div></span><span class='col-lg-3 col-md-3 col-sm-3 col-3 text-center d-inline-block p-0 pr-4'><div class='rounded_digit py-3'><span id='minutes' class='d-block te_days_hr_min_sec_digit text-black'>"+minutes+"</span><span id='m_lbl' class=' d-block'>Mins</span></div></span><span class='col-lg-3 col-md-3 col-sm-3 col-3 text-center d-inline-block p-0 pr-4'><div class='rounded_digit py-3'><span id='seconds' class='d-block te_days_hr_min_sec_digit text-black'>"+seconds+"</span><span id='s_lbl' class='d-block'>Secs</span></div></span></div>";
                    $('.timer_data').append(append_data)
                }
                else {
                    $('.timer_data').empty()
                }
            }, 1000);
        }
    },
});
});
