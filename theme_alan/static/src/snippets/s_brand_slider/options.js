odoo.define('theme_alan.s_brand_slider_options',function(require){
'use strict';

var core = require('web.core');
var rpc = require('web.rpc');
var options = require('web_editor.snippets.options');
var wUtils = require('website.utils');
var _t = core._t;

options.registry['brand_slider_actions'] = options.Class.extend({
    popup_template_id: 'main_brand_slider_layout_template',
    popup_title: _t('Select Brand Collection'),

    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    brand_slider_configure: function (previewMode, value) {
        var self = this;
        var def = wUtils.prompt({
            'id': this.popup_template_id,
            'window_title': this.popup_title,
            'select': _t('Brand Collection'),
            'init': function (field, dialog) {
                return rpc.query({
                    model: 'slider_brand.collection.configure',
                    method: 'name_search',
                    args: ['', [['website_id','in',[false,parseInt($('html').attr('data-website-id'))]],['active','=',true]]],
                    context: self.options.recordInfo.context,
                }).then(function (data) {
                    $(dialog).find('.btn-primary').prop('disabled', !data.length);
                    return data;
                });
            },
        });
        def.then(function (result) {
            var collection_id = parseInt(result.val);
            self.$target.attr('data-collection_id', collection_id);
            rpc.query({
                model: 'slider_brand.collection.configure',
                method: 'read',
                args: [[collection_id],['name']],
            }).then(function (data){
                if(data && data[0] && data[0].name){
                    var collection_name = data[0].name;
                    self.$target.attr('data-collection_name', collection_name);
                    self.$target.empty().append('<div class="seaction-head"><h2>'+ collection_name +'</h2></div>');
                } else {
                    var collection_name = 'No Collection Selected';
                }
            });
        });
        return def;
    },
    onBuilt: function () {
        var self = this;
        this._super();
        this.brand_slider_configure('click');
    },
    cleanForSave: function () {
        this.$target.empty();
        $('.as_brand_slider').empty();
        var model = this.$target.parent().attr('data-oe-model');
        if(model){
            this.$target.parent().addClass('o_editable o_dirty');
        }
    },
});
});
