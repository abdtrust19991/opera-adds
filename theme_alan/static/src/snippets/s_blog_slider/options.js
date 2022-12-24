odoo.define('theme_alan.s_blog_slider_options',function(require){
'use strict';

var core = require('web.core');
var rpc = require('web.rpc');
var options = require('web_editor.snippets.options');
var wUtils = require('website.utils');
var _t = core._t;

options.registry['latest_blog'] = options.Class.extend({
    popup_template_id: 'editor_new_blog_slider_template',
    popup_title: _t('Select Collection'),
    website_blog_configure: function (previewMode, value) {
        var self = this;
        var def = wUtils.prompt({
            'id': this.popup_template_id,
            'window_title': this.popup_title,
            'select': _t('Collection'),
            'init': function (field, dialog) {
                return rpc.query({
                    model: 'blog.configure',
                    method: 'name_search',
                    args: ['', []],
                    context: self.options.recordInfo.context,
                }).then(function (data) {
                    $(dialog).find('.btn-primary').prop('disabled', !data.length);
                    return data;
                });
            },
        });
        def.then(function (result) {
            var collection_id = parseInt(result.val);
            self.$target.attr('data-blog_list-id', collection_id);
            rpc.query({
                model: 'blog.configure',
                method: 'read',
                args: [[collection_id],['name']],
            }).then(function (data){
                if(data && data[0] && data[0].name)
                    self.$target.empty().append('<div class="seaction-head"><h2>'+ data[0].name+'</h2></div>');
            });
        });
        return def;
    },
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    onBuilt: function () {
        var self = this;
        this._super();
        this.website_blog_configure('click').guardedCatch(function () {
            self.getParent()._onRemoveClick($.Event( 'click' ));
        });
    },
    cleanForSave: function(){
        this.$target.empty();
        $('.web_blog_slider').empty();
        var model = this.$target.parent().attr('data-oe-model');
        if(model){
            this.$target.parent().addClass('o_editable o_dirty');
        }
    },
});
});
