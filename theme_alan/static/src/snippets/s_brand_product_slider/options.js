odoo.define('theme_alan.s_brand_product_slider_options',function(require){
'use strict';

var core = require('web.core');
var rpc = require('web.rpc');
var options = require('web_editor.snippets.options');
var wUtils = require('website.utils');
var _t = core._t;
var weContext = require('web_editor.context');

options.registry['brand_product_slider_actions'] = options.Class.extend({
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    popup_template_id: 'brand_product_slider_layout_template',
    popup_title: _t('Select Slider Layout'),
    brand_product_slider_configure: function (previewMode, value) {
            var self = this;
            var def = wUtils.prompt({
                'id': this.popup_template_id,
                'window_title': this.popup_title,
                'select': _t('Slider Layout'),

                'init': function (field) {
                    var $form = this.$dialog.find('div.form-group');
                    $form.prepend('<label class="col-md-4 col-form-label">Select Brand:</label><div class="width_div col-md-8"><select multiple class="form-control" id="slider_brand_option" style="height:59px;"></select></br></div>');
                    var slider_styles = rpc.query({
                        model: 'as.product.brand',
                        method: 'name_search',
                        args: ['', [['website_id','in',[false,parseInt($('html').attr('data-website-id'))]],['active','=',true]]],
                        context: weContext.get(),
                    });
                    slider_styles.then(function (data) {
                        var selectedBrands = self.$target.attr('data-slider-brand-id');
                        if(selectedBrands != undefined && selectedBrands != ''){
                            var selBrandLst = $.map(selectedBrands.split(','), function(value){
                                return parseInt(value);
                            });
                            $.each(data, function(key, value) {
                                var isSelected = selBrandLst.includes(value[0])
                                if(isSelected === true){
                                    $('#slider_brand_option').append($("<option selected></option>").attr("value",value[0]).text(value[1]));
                                }else{
                                    $('#slider_brand_option').append($("<option></option>").attr("value",value[0]).text(value[1]));
                                }
                            });
                        }
                        else{
                            $.each(data, function(key, value) {
                                $('#slider_brand_option').append($("<option></option>").attr("value",value[0]).text(value[1]));
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
                if(dialog){
                    rpc.query({
                        model: 'product_slider_common.options',
                        method: 'read',
                        args: [[style_id],['name']],
                    }).then(function (data){
                        if(data && data[0] && data[0].name){
                            var collection_name = data[0].name;
                            var getSelCats = self.$target.attr('data-slider-brand-id');
                            if(getSelCats == undefined || getSelCats == ''){
                                self.$target.find('div').empty().append('<div class="seaction-head"><h2>No Brands Selected! </h2></div>');
                            }else{
                                self.$target.attr('data-slider-style-name',collection_name);
                                self.$target.find('div').empty().append('<div class="seaction-head"><h2>Brand Product Slider: '+ collection_name  +'</h2></div>');
                            }

                        } else {
                            collection_name = 'NO LAYOUT SELECTED';
                        }
                    });
                    var brand_ids = dialog.find('#slider_brand_option').val();
                    self.$target.attr('data-slider-brand-id', brand_ids);
                    self.$target.attr('data-slider-style-id', data.val);
                }
            });
        return def;
    },
    onBuilt: function(){
        var self = this;
        this._super();
        this.brand_product_slider_configure('click').guardedCatch(function () {
            self.getParent()._onRemoveClick($.Event( 'click' ));
        });
    },
    cleanForSave: function () {
        this.$target.find('div').empty();
        $('.as_brand_product').find('div').empty();
        var model = this.$target.parent().attr('data-oe-model');
        if(model){
            this.$target.parent().addClass('o_editable o_dirty');
        }
    },
});
});
