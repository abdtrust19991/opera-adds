odoo.define('theme_alan.s_product_var_slider_options',function(require){
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var weContext = require('web_editor.context');
var options = require('web_editor.snippets.options');

var qweb = core.qweb;
var _t = core._t;

ajax.loadXML('/theme_alan/static/src/xml/product_variant_slider_popup.xml', core.qweb);

options.registry['product_variant_slider_actions'] = options.Class.extend({
    popup_template_id: 'main_product_variant_slider_layout_template',
    popup_title: _t('Select Product Variant Slider Layout'),

    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },

    initialize_owl: function (autoplay=false, items=4, slider_timing=6, is_infinite=false) {
        if(slider_timing > 10){
            var slider_timing = 6000
        }else{
            var slider_timing = parseInt(slider_timing) * 1000;
            var slider_timing = slider_timing == 0 ? 6000 : slider_timing;
        }
        is_infinite = is_infinite == 'true' ? true : false;

        $('.as-product-var-carousel').owlCarousel({
            loop: is_infinite,
            rewind: true,
            margin: 10,
            nav: true,
            lazyLoad:true,
            dots: false,
            navText : ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
            autoplay: autoplay,
            autoplaySpeed: 1000,
            autoplayTimeout:slider_timing,
            autoplayHoverPause:true,
            items: items,
            responsive: {
                0: {
                    items: 1,
                },
                481: {
                    items: 2,
                },
                768: {
                    items: 2,
                },
                1024: {
                    items: 4,
                },
                1200: {
                    items: items,
                }
            },
        });
    },
    initialize_slider_preview:function($modal, collection_ids, slider_type){
        var self = this;
        self._rpc({
            route: '/shop/get_product_variant_snippet_slider_view',
            params: {
                'collection':collection_ids,
                'slider':slider_type
            }
        }).then(function (preview) {
            if(preview != false){
                $modal.find('.p_slider_sample_view').empty().append(preview['config_preview']);
                $modal.find('.as_collection_change').first().addClass('active');

                var autoplay = self.$target.attr('data-prod-auto') || false;
                var prod_count = parseInt(self.$target.attr('data-prod-count')) || 4;
                var slider_timing = parseInt(self.$target.attr('data-slider_timing')) || 0;

                var is_infinite = self.$target.attr('data-is_infinite') || false;
                self.initialize_owl(eval(autoplay), prod_count, slider_timing,is_infinite);

                var $add_to_cart = $modal.find('#add_to_cart');
                var $quick_view = $modal.find('#quick_view');
                var $pro_compare = $modal.find('#pro_compare');
                var $pro_wishlist = $modal.find('#pro_wishlist');
                var $pro_ribbon = $modal.find('#pro_ribbon');
                var $pro_ratting = $modal.find('#pro_ratting');

                $add_to_cart.is(':checked') == true ? $modal.find(".as-btn-cart").css("display","block") : $modal.find(".as-btn-cart").css("display","none");
                $quick_view.is(':checked') == true ? $modal.find(".o_quick_view").css("display","block") : $modal.find(".o_quick_view").css("display","none");
                $pro_compare.is(':checked') == true ? $modal.find(".o_add_compare").css("display","block") : $modal.find(".o_add_compare").css("display","none");
                $pro_wishlist.is(':checked') == true ? $modal.find(".o_add_wishlist").css("display","block") : $modal.find(".o_add_wishlist").css("display","none");
                $pro_ribbon.is(':checked') == true ? $modal.find(".ribbon-style-1").css("display","block") : $modal.find(".ribbon-style-1").css("display","none");
                $pro_ratting.is(':checked') == true ? $modal.find(".prod_rating").css("display","block") : $modal.find(".prod_rating").css("display","none");
            }
            else{
                $modal.find('.p_slider_sample_view').empty();
            }
        });
    },
    product_variant_slider_configure: function(previewMode, value){
        var self = this;

        var $modal = $(qweb.render('theme_alan.p_var_slider_popup_template'));
        $modal.modal();

        self._rpc({
            model: 'slider_var.collection.configure',
            method: 'name_search',
            args: ['', [['website_id','in',[false,parseInt($('html').attr('data-website-id'))]]]],
        }).then(function(collection){
                var pro_col_ele =  $modal.find('select[name="pro_collection"]');
                if(collection.length > 0){
                    for(var i = 0; i < collection.length; i++){
                        pro_col_ele.append("<option value='" + collection[i][0] + "'>" + collection[i][1] + "</option>");
                    }
                }
                var selected_collection = self.$target.attr('data-collection_id');
                selected_collection = selected_collection.split(',');
                $modal.find('#multiselect_two').multiselect('select',selected_collection);

                self._rpc({
                    model: 'product_var_slider.options',
                    method: 'name_search',
                    args: ['', []],
                    context: weContext.get()
                }).then(function(slider){
                    var $sliders_ele =  $modal.find('select[name="slider_type"]');
                    if(slider.length > 0){
                        var slider = slider.sort((a,b) => a[1].toUpperCase().localeCompare(b[1].toUpperCase()));
                        for(var i = 0; i < slider.length; i++){
                            if(slider[i][0] == '5' || slider[i][0] == '6' || slider[i][0] == '7'){
                                $sliders_ele.append("<option class='grid_style' value='slider_layout_" + slider[i][0] + "'>" + slider[i][1] + "</option>");
                            }else{
                                $sliders_ele.append("<option class='slider_style' value='slider_layout_" + slider[i][0] + "'>" + slider[i][1] + "</option>");
                            }
                        }
                    }
                    var selected_slider = self.$target.attr('data-slider_type');
                    $sliders_ele.val(selected_slider);
                    var collection_ids =  $modal.find('#multiselect_two').val();
                    var slider_type =  $sliders_ele.val();
                    if (slider_type == 'slider_layout_5' || slider_type == 'slider_layout_6' || slider_type == 'slider_layout_7') {
                        var $prod_auto = $modal.find('#prod-auto');
                        $prod_auto.prop('checked',false);
                        if(slider_type == 'slider_layout_5'){
                            $modal.find(".pro_ratting").css("display","none");
                        }
                        $modal.find('div.is_infinite').hide();
                        self.$target.attr('data-prod-auto',false);
                        $modal.find('#slider_time').val(5);
                        $modal.find('div.for_slider_only').hide();
                        $modal.find('div.prod_count').hide();
                        $modal.find("#display_type").val('grid');
                        $modal.find(".slider_style").css('display','none');
                    }
                    else{
                        $modal.find('div.for_slider_only').show();
                        $modal.find('div.prod_count').show();
                        $modal.find("#display_type").val('slider');
                        $modal.find(".grid_style").css('display','none');
                    }
                    self.initialize_slider_preview($modal,collection_ids,slider_type);
                });
        });

        $modal.on('click', '.btn_apply', function(e){
            e.preventDefault();
            var $collection_list = $modal.find("select[name='pro_collection']");
            var $slider_ele = $modal.find("select[name='slider_type']");
            var $prod_count = $modal.find('#prod-count');
            var $prod_auto = $modal.find('#prod-auto');
            var $slider_time = $modal.find('#slider_time');
            var $add_to_cart = $modal.find('#add_to_cart');
            var $quick_view = $modal.find('#quick_view');
            var $pro_compare = $modal.find('#pro_compare');
            var $pro_wishlist = $modal.find('#pro_wishlist');
            var $pro_ribbon = $modal.find('#pro_ribbon');
            var $pro_ratting = $modal.find('#pro_ratting');

            $prod_auto.is(':checked') == true ? self.$target.attr('data-prod-auto', true) :  self.$target.attr('data-prod-auto', false);
            $add_to_cart.is(':checked') == true ? self.$target.attr('data-add_to_cart', true) : self.$target.attr('data-add_to_cart', false);
            $quick_view.is(':checked') == true ? self.$target.attr('data-quick_view', true) : self.$target.attr('data-quick_view', false);
            $pro_compare.is(':checked') == true ? self.$target.attr('data-pro_compare', true) : self.$target.attr('data-pro_compare', false);
            $pro_wishlist.is(':checked') == true ? self.$target.attr('data-pro_wishlist', true) : self.$target.attr('data-pro_wishlist', false);
            $pro_ribbon.is(':checked') == true ? self.$target.attr('data-pro_ribbon', true) : self.$target.attr('data-pro_ribbon', false);
            $pro_ratting.is(':checked') == true ? self.$target.attr('data-pro_ratting', true) : self.$target.attr('data-pro_ratting', false);

            self.$target.attr('data-collection_id', $collection_list.val());
            self.$target.attr('data-slider_type', $slider_ele.val());
            self.$target.attr('data-prod-count', $prod_count.val());
            self.$target.attr('data-slider_timing', $slider_time.val());

            var collection_name = $modal.find("select[name='pro_collection'] option:selected").text();
            if(!collection_name)
                collection_name = 'NO COLLECTION SELECTED';
            self.$target.attr('data-collection_name', collection_name);
            self.$target.find('div').empty().append('<div class="seaction-head"><h2>' + collection_name + '</h2></div>');

        });

        $modal.on('change','#prod-count', function(e){
            e.preventDefault();
            self.$target.attr('data-prod-count',$(this).val());
            var collection_ids =  $modal.find('select[name="pro_collection"]').val();
            var slider_type =  $modal.find('select[name="slider_type"]').val();
            self.initialize_slider_preview($modal,collection_ids,slider_type);
            $modal.find('#prod_count_val').empty().text($(this).val());
        });

        $modal.on('change','#display_type', function(e){
            e.preventDefault();
            var style = $(this).val();
            if(style == 'grid'){
                $modal.find(".slider_style").css('display','none');
                $modal.find(".grid_style").css('display','block');
                $modal.find("#slider_type").val('slider_layout_5').trigger('change');
            }else{
                $modal.find(".grid_style").css('display','none');
                $modal.find(".slider_style").css('display','block');
                $modal.find("#slider_type").val('slider_layout_1').trigger('change');
            }

        });

        $modal.on('change','#multiselect_two',function(e){
            e.preventDefault();
            var collection_ids =  $(this).val();
            var slider_type = $modal.find('#slider_type').val();
            self.initialize_slider_preview($modal,collection_ids,slider_type);
        });
        $modal.on('click','.as-edit-popup-action',function(ev){
            ev.preventDefault();
            var $input = $(this).children().first();
            var is_checked = $input.is(':checked');
            if(is_checked == true){
                $input.prop('checked',false);
                is_checked = false;
            }else{
                $input.prop('checked',true);
                is_checked = true;
            }
            switch ($input.attr('name')) {
                case 'add_to_cart':
                    is_checked == true ? $modal.find(".as-btn-cart").css("display","block") : $modal.find(".as-btn-cart").css("display","none");
                    break;
                case 'quick_view':
                    is_checked == true ? $modal.find(".o_quick_view").css("display","block") : $modal.find(".o_quick_view").css("display","none");
                    break;
                case 'pro_compare':
                    is_checked == true ? $modal.find(".o_add_compare").css("display","block") : $modal.find(".o_add_compare").css("display","none");
                    break;
                case 'pro_wishlist':
                    is_checked == true ? $modal.find(".o_add_wishlist").css("display","block") : $modal.find(".o_add_wishlist").css("display","none");
                    break;
                case 'pro_ribbon':
                    is_checked == true ? $modal.find(".ribbon-style-1").css("display","block") : $modal.find(".ribbon-style-1").css("display","none");
                    break;
                case 'pro_ratting':
                    is_checked == true ? $modal.find(".prod_rating").css("display","block") : $modal.find(".prod_rating").css("display","none");
                    break;
                case 'is_infinite':
                    is_checked == true ? self.$target.attr('data-is_infinite',true) : self.$target.attr('data-is_infinite',false);
                    var collection_ids =  $modal.find('select[name="pro_collection"]').val();
                    var get_slider = $modal.find('#slider_type').val();
                    self.initialize_slider_preview($modal,collection_ids,get_slider);
                    break
            }
        });

        $modal.on('change', '#slider_time', function (e){
            e.preventDefault();
            var collection_ids =  $modal.find('select[name="pro_collection"]').val();
            var get_slider = $modal.find('#slider_type').val();
            self.$target.attr('data-slider_timing',$(this).val())
            self.initialize_slider_preview($modal,collection_ids,get_slider);
            $modal.find('#slider_time_val').empty().text($(this).val());
        });

        $modal.on('change', '#slider_type', function (e){
            e.preventDefault();
            var collection_ids =  $modal.find('select[name="pro_collection"]').val();
            var $prod_auto = $modal.find('#prod-auto');
            var $is_infi =  $modal.find('#is_infinite');
            var get_slider = $(this).val();
            get_slider == 'slider_layout_5' ? $modal.find('.pro_ratting').css('display','none'): $modal.find('.pro_ratting').css('display','block');
            if (get_slider == 'slider_layout_5' || get_slider == 'slider_layout_6' || get_slider == 'slider_layout_7') {
                $prod_auto.prop('checked',false);
                $is_infi.prop('checked',false);
                self.$target.attr('data-prod-auto',false);
                self.$target.attr('data-is_infinite',false)
                $modal.find('#slider_time').val(5);
                $modal.find('div.for_slider_only').hide();
                $modal.find('div.prod_count').hide();
                $modal.find('div.is_infinite').hide();
            }
            else{
                $modal.find('div.for_slider_only').show();
                $modal.find('div.prod_count').show();
                $modal.find('div.is_infinite').show();
                $prod_auto.prop('checked') == true ? $modal.find('.slider_time').show() : $modal.find('.slider_time').hide();
            }
            self.initialize_slider_preview($modal,collection_ids,get_slider);
        });

        $modal.on('change', "#prod-auto", function(e){
            e.preventDefault();
            if ($modal.find('input#prod-auto').is(':checked')) {
                self.$target.attr('data-prod-auto',true);
                $modal.find('.slider_time').show();
                $modal.find('#slider_time').val(self.$target.attr('data-slider_timing'));
            }
            else {
                self.$target.attr('data-prod-auto',false);
                $modal.find('.slider_time').hide();
                $modal.find('#slider_time').val(5);
            }
            var collection_ids =  $modal.find('select[name="pro_collection"]').val();
            var slider_type =  $modal.find('select[name="slider_type"]').val();
            self.initialize_slider_preview($modal,collection_ids,slider_type);
        });

        self.$target.attr('data-prod-auto') == 'true' ? $modal.find("form input[id='prod-auto']").prop('checked', true) : $modal.find("form input[id='prod-auto']").prop('checked', false);
        self.$target.attr('data-add_to_cart') == 'true' ? $modal.find("form input[id='add_to_cart']").prop('checked', true) : $modal.find("form input[id='add_to_cart']").prop('checked', false);
        self.$target.attr('data-quick_view') == 'true' ? $modal.find("form input[id='quick_view']").prop('checked', true) :  $modal.find("form input[id='quick_view']").prop('checked', false);
        self.$target.attr('data-pro_compare') == 'true' ? $modal.find("form input[id='pro_compare']").prop('checked', true) : $modal.find("form input[id='pro_compare']").prop('checked', false);
        self.$target.attr('data-pro_wishlist') == 'true' ? $modal.find("form input[id='pro_wishlist']").prop('checked', true) : $modal.find("form input[id='pro_wishlist']").prop('checked', false);
        self.$target.attr('data-pro_ribbon') == 'true' ? $modal.find("form input[id='pro_ribbon']").prop('checked', true) : $modal.find("form input[id='pro_ribbon']").prop('checked', false);
        self.$target.attr('data-pro_ratting') == 'true' ? $modal.find("form input[id='pro_ratting']").prop('checked', true) : $modal.find("form input[id='pro_ratting']").prop('checked', false);
        self.$target.attr('data-is_infinite') == 'true' ? $modal.find("form input[id='is_infinite']").prop('checked', true) : $modal.find("form input[id='is_infinite']").prop('checked', false);
        self.$target.attr('data-prod-auto') == 'true' ? $modal.find('.slider_time').show() : $modal.find('.slider_time').hide();
        $modal.find('#prod-count').val(self.$target.attr('data-prod-count'));
        $modal.find('#slider_time').val(self.$target.attr('data-slider_timing'));

        $modal.find('#prod_count_val').empty().text($modal.find('#prod-count').val());
        $modal.find('#slider_time_val').empty().text($modal.find('#slider_time').val());
    },
    onBuilt: function(){

        var self = this;
        this._super();
        this.product_variant_slider_configure('click');
    },
    cleanForSave: function () {
        this.$target.find('div').empty();
        $('.as_product_slider').find('div').empty();
        var model = this.$target.parent().attr('data-oe-model');
        if(model){
            this.$target.parent().addClass('o_editable o_dirty');
        }
    },
});
});