odoo.define('theme_alan.s_offer_timer_options',function(require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var web_editor = require('web_editor.editor');
var options = require('web_editor.snippets.options');
var wUtils = require('website.utils');
var qweb = core.qweb;

ajax.loadXML('/theme_alan/static/src/xml/timer_snippets.xml', core.qweb);

options.registry['offer_timer'] = options.Class.extend({
    modify_date : function(previewMode, value){
        var self = this;
        if(previewMode === false || previewMode === 'click'){
            self.$modal = $(qweb.render('theme_alan.p_offer_timer_snippet'));
            $('body > #offer_timer_modal').remove();
            self.$modal.appendTo('body');
            self.$modal.on('click', '.btn_continue', function(){
                var $timer_val = self.$modal.find('#timer_val');
                var date = new Date($timer_val.val());
                if(date){
                    self.$target.attr('data-date', date);
                }
                else{
                    self.$target.attr('data-date','nan');
                }
            });
            self.$modal.modal();
        }
        return self;
    },
    onBuilt: function () {
        var self = this;
        this._super();
        this.modify_date('click');
    },
    cleanForSave: function () {
        this.$target.empty();
        $('.offer_timer').empty();
        var model = this.$target.parent().attr('data-oe-model');
        if(model){
            this.$target.parent().addClass('o_editable o_dirty');
        }
    },
});
});
