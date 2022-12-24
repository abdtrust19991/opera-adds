odoo.define('theme_alan.s_category_product_slider_options',function(require){
'use strict';

var core = require('web.core');
var rpc = require('web.rpc');
var options = require('web_editor.snippets.options');
var wUtils = require('website.utils');
var _t = core._t;
var weContext = require('web_editor.context');

options.registry['category_product_slider_actions'] = options.Class.extend({
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    popup_template_id: 'category_product_slider_layout_template',
    popup_title: _t('Select Slider Layout'),
    category_product_slider_configure: function (previewMode, value) {
        var self = this;
        var def = wUtils.prompt({
            'id': this.popup_template_id,
            'window_title': this.popup_title,
            'select': _t('Slider Layout'),
            'init': function (field, dialog) {
                return rpc.query({
                    model: 'product_slider_common.options',
                    method: 'name_search',
                    args: ['', []],
                    context: self.options.recordInfo.context,
                }).then(function (data) {
                    $(dialog).find('.btn-primary').prop('disabled', !data.length);
                    return data;
                });
            },
            'init': function (field) {
                var $form = this.$dialog.find('div.form-group');
                $form.prepend('<label class="col-md-4 col-form-label">Select Category:</label><div class="width_div col-md-8"><select multiple class="form-control" id="slider_category_option"></select></div>');
                var slider_styles = rpc.query({
                    model: 'product.public.category',
                    method: 'name_search',
                    args: ['', [['website_id','in',[false,parseInt($('html').attr('data-website-id'))]]]],
                    context: weContext.get(),
                });
                slider_styles.then(function (data) {
                    var selectedCat = self.$target.attr('data-slider-category-id');
                    if(selectedCat != undefined && selectedCat != ''){
                        var selCatLst = $.map(selectedCat.split(','), function(value){
                            return parseInt(value);
                        });
                        $.each(data, function(key, value) {
                            var isSelected = selCatLst.includes(value[0])
                            if(isSelected === true){
                                $('#slider_category_option').append($("<option selected></option>").attr("value",value[0]).text(value[1]));
                            }else{
                                $('#slider_category_option').append($("<option></option>").attr("value",value[0]).text(value[1]));
                            }
                        });
                    }
                    else{
                        $.each(data, function(key, value) {
                            $('#slider_category_option').append($("<option></option>").attr("value",value[0]).text(value[1]));
                        });
                    }
                });
                return rpc.query({
                    model: 'product_slider_common.options',
                    method: 'name_search',
                    context: weContext.get(),
                }).then(function (data) {
                    data.sort((a, b) => {
                        return a[1].localeCompare(b[1]);
                    });
                    return data
                });
            },
        });
        def.then(function (data) {
            var style_id = parseInt(data.val);
            var dialog = data.dialog;
            if(dialog)
            {
                rpc.query({
                    model: 'product_slider_common.options',
                    method: 'read',
                    args: [[style_id],['name']],
                }).then(function (data){
                    if(data && data[0] && data[0].name){
                        var collection_name = data[0].name;
                        var getSelCats = self.$target.attr('data-slider-category-id');
                        if(getSelCats == undefined || getSelCats == ''){
                            self.$target.find('div').empty().append('<div class="seaction-head"><h2>No Category Selected!</h2></div>');
                        }else{
                            self.$target.attr('data-slider-style-name',collection_name);
                            self.$target.find('div').empty().append('<div class="seaction-head"><h2>Category Product Slider: '+ collection_name  +'</h2></div>');
                        }

                    } else {
                        collection_name = 'NO LAYOUT SELECTED';
                    }
                });
                var category_ids = dialog.find('#slider_category_option').val();
                self.$target.attr('data-slider-category-id', category_ids);
                self.$target.attr('data-slider-style-id', data.val);
            }
        });
        return def;
    },
    onBuilt: function(){
        var self = this;
        this._super();
        this.category_product_slider_configure('click').guardedCatch(function () {
            self.getParent()._onRemoveClick($.Event( 'click' ));
        });
    },
    cleanForSave: function () {
        this.$target.find('div').empty();
        $('.as_category_product').find('div').empty();
        var model = this.$target.parent().attr('data-oe-model');
        if(model){
            this.$target.parent().addClass('o_editable o_dirty');
        }
    },
});
});
