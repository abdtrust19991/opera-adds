odoo.define('theme_alan.s_product_banner_options', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var options = require('web_editor.snippets.options');
var qweb = core.qweb;
var _t = core._t;

ajax.loadXML('/theme_alan/static/src/xml/product_banner_popup.xml', core.qweb);
options.registry['product_banner_actions'] = options.Class.extend({
    start:function(){
        return this._super.apply(this, arguments);
    },
    product_banner_configure:function(){
        var self = this;
        self.$modal = $(qweb.render('theme_alan.product_banner_popup_template',
                        {   apply:_t('Apply'),
                            close:_t('Close'),
                            title:_t('Configure Special Product'),
                            find_product:_t('Find Product'),
                            optional_btn:_t('Optional Button'),
                            snp_pos:_t('Position'),
                        }));
        $(self.$modal).appendTo('body');
        self.$modal.modal();
        var formatState = function(state){
            if(!state.id){
                return state.text
            }
            var optimage = $(state.element).attr('data-image');
            var $state = $(
                '<span><img src="'+optimage+'" width="40" class="mr-3" />' + state.text + '</span>'
                );
            return $state;
        }
        var $selectionfield = self.$modal.find('#search_product');
        self._rpc({
            route: '/get/all_product/',
            params: {}
        }).then(function (result) {
            $selectionfield.append('<option></option>');
            for (const prod of result) {
                var opt = "<option value='"+ prod['id'] +"' data-image='"+prod.image_url+"'>"+ prod['text'] +"</option>"
                $selectionfield.append(opt);
            }
        });
        $selectionfield.select2({
            width:'100%',
            formatResult:formatState,
        })
        if(self.$target.attr('data-sp_id') != '0,'){
            var id = self.$target.attr('data-sp_id')
            var name = self.$target.attr('data-sp_name')
            if(name != 'NO PRODUCT SELECTED'){
                var selectedid = id.split(',');
                var selectedname = name.split(',');
                var selected_data = [];
                for (var i = 0; i < selectedid.length; i++) {
                    if(selectedid[i] != ''){
                        selected_data.push({'id':selectedid[i],'text':selectedname[i]});
                    }
                }
                $selectionfield.select2('data',selected_data);
            }
            self.$target.empty().append('<div class="container"><div class="seaction-head"><h2>'+ self.$target.attr('data-sp_name') +'</h2></div></div>');
        };
        if(self.$target.attr('data-add_to_cart') == 1){
            var $add_to_cart = self.$modal.find('#add_to_cart');
            $add_to_cart.attr('checked',true);
        };
        if(self.$target.attr('data-buy_btn') == 1){
            var $pro_buy_btn = self.$modal.find('#pro_buy_btn');
            $pro_buy_btn.attr('checked',true);
        };
        if(self.$target.attr('data-prod_rating') == 1){
            var $pro_rating = self.$modal.find('#pro_rating');
            $pro_rating.attr('checked',true);
        };
        if(self.$target.attr('data-prob_label') == 1){
            var $pro_label = self.$modal.find('#pro_label');
            $pro_label.attr('checked',true);
        };
        if(self.$target.attr('data-pos') == '0'){
            var $pos_left = self.$modal.find('#pos_left');
            $pos_left.attr('checked',true);
        }else{
            var $pos_right = self.$modal.find('#pos_right');
            $pos_right.attr('checked',true);
        }
        self.$modal.on('change', $selectionfield,function (e) {
            var data = $selectionfield.select2('data');
            var cur_id = '';
            var cur_name = '';
            for (const prod of data) {
                if(prod['id'] != ''){
                    cur_id += prod['id'] + ','
                    cur_name += prod['text'] + ','
                }
            }
            if(cur_id == '' || cur_name == ''){
                self.$target.attr('data-sp_id','0');
                self.$target.attr('data-sp_name','NO PRODUCT SELECTED');
            }
            else{
                self.$target.attr('data-sp_id',cur_id);
                self.$target.attr('data-sp_name',cur_name);
            }
        });

        self.$modal.on('click','.submit_btn',function (e) {
            e.preventDefault();
            var $add_to_cart = self.$modal.find('#add_to_cart');
            var $pro_buy_btn = self.$modal.find('#pro_buy_btn');
            var $pro_rating = self.$modal.find('#pro_rating');
            var $pro_label = self.$modal.find('#pro_label');
            var $position = self.$modal.find("input[name='pos_snippet']:checked");
            if($position.val() != undefined){
                self.$target.attr('data-pos', $position.val());
            };
            var add_to_cart = $add_to_cart.is(':checked') ? 1 : 0;
            var pro_buy_btn = $pro_buy_btn.is(':checked') ? 1 : 0;
            var pro_rating = $pro_rating.is(':checked') ? 1 : 0;
            var pro_label = $pro_label.is(':checked') ? 1 : 0;

            var data = $selectionfield.select2('data');
            var cur_id = '';
            var cur_name = '';
            for (const prod of data) {
                if(prod['id'] != ''){
                    cur_id += prod['id'] + ','
                    cur_name += prod['text'] + ','
                }
            }
            if(cur_id == '' || cur_name == ''){
                self.$target.attr('data-sp_id','0');
                self.$target.attr('data-sp_name','NO PRODUCT SELECTED');
                self.$target.empty().append('<div class="container"><div class="seaction-head"><h2>'+ self.$target.attr('data-sp_name') +'</h2></div></div>');
            }
            else{
                self.$target.attr('data-sp_id',cur_id);
                self.$target.attr('data-sp_name', cur_name);
            }
            self.$target.attr('data-add_to_cart', add_to_cart);
            self.$target.attr('data-buy_btn', pro_buy_btn);
            self.$target.attr('data-prod_rating', pro_rating);
            self.$target.attr('data-prob_label', pro_label);

            if(self.$target.attr('data-sp_id') != '0'){
                return self._rpc({
                    route: '/get/product_banner/',
                    params: {
                        'id':self.$target.attr('data-sp_id'),
                        'edit_mode':true
                    }
                }).then(function (result) {
                    self.$target.attr('data-sp_name', result['prod_list']);
                    self.$target.empty().append('<div class="container"><div class="seaction-head"><h2>'+ result['prod_list']  +'</h2></div></div>');
                });
            };
        });
    },
    onBuilt: function(){
        this._super();
        this.product_banner_configure('click');
    },
    cleanForSave: function () {
        this.$target.empty();
        $('.as_product_banner_slider').empty();
        var model = this.$target.parent().attr('data-oe-model');
        if(model){
            this.$target.parent().addClass('o_editable o_dirty');
        }
    },
});
});
