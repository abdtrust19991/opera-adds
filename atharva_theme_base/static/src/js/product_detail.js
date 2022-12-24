odoo.define('atharva_theme_base.product_detail_js', function (require) {
"use strict";

var VariantMixin = require('sale.VariantMixin');
var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;
var xml_load = ajax.loadXML(
    '/website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml',
    QWeb
);

publicWidget.registry.StickProductMedia = publicWidget.Widget.extend({
    selector:'#wrapwrap',
    events:{
        'click #add_to_cart_cp_btn':'_add_to_cart_click',
        'click #buy_now_cp_btn':'_buy_btn_click',
        'click .mm-hb-level-1 > .cat-level-title .mob_menu':'_megaMenuClass',
        'click .mm-hb-level-2 > .ul-lever > .mm-label > .cat-level-title .mob_menu':'_megaMenuClass2',
        'click .h-col-mobile-h-search > a':'_searchBarForMobile'
    },
    _megaMenuClass:function(ev){
        $(ev.currentTarget).parents("li.mm-hb-level-1:first").toggleClass("open")
    },
    _megaMenuClass2:function(ev){
        $(ev.currentTarget).parents(".mm-hb-level-2 li.mm-label:first").toggleClass("open")
    },
    _searchBarForMobile:function(ev){
        $(".header-search-mobile").toggleClass("open-search");
    },
    _add_to_cart_click:function(){
        var cartbtn = $('#add_to_cart').hasClass('disabled out_of_stock');
        if(cartbtn != true ){
            $('#add_to_cart').trigger('click');
        }
    },
    _buy_btn_click:function(){
        var buyBtn = $('#buy_now').hasClass('disabled out_of_stock');
        if(buyBtn != true ){
            $('#buy_now').trigger('click');
        }
    },
    start:function(){
        this._stickyButtonAccessability()
    },
    _stickyButtonAccessability:function(){
        var cartbtn = $('#add_to_cart').hasClass('disabled out_of_stock');
        var buyBtn = $('#buy_now').hasClass('disabled out_of_stock');
        if(cartbtn == true || buyBtn == true){
            $("#add_to_cart_cp_btn").addClass("disabled");
            $("#buy_now_cp_btn").addClass("disabled");
        }else{
            $("#add_to_cart_cp_btn").removeClass("disabled");
            $("#buy_now_cp_btn").removeClass("disabled");
        }
    }
});

VariantMixin._onChangeCombinationStockCustom = function (ev, $parent, combination) {
        var product_id = 0;

        // needed for list view of variants
        if ($parent.find('input.product_id:checked').length) {
            product_id = $parent.find('input.product_id:checked').val();
        } else {
            product_id = $parent.find('.product_id').val();
        }
        var isMainProduct = combination.product_id &&
            ($parent.is('.js_main_product') || $parent.is('.main_product')) &&
            combination.product_id === parseInt(product_id);

        if (!this.isWebsite || !isMainProduct){
            return;
        }

        var qty = $parent.find('input[name="add_qty"]').val();

        $parent.find('#add_to_cart').removeClass('out_of_stock');
        $parent.find('#buy_now').removeClass('out_of_stock');
        if (combination.product_type === 'product' && _.contains(['always', 'threshold'], combination.inventory_availability)) {
            combination.virtual_available -= parseInt(combination.cart_qty);
            if (combination.virtual_available < 0) {
                combination.virtual_available = 0;
            }
            // Handle case when manually write in input
            if (qty > combination.virtual_available) {
                var $input_add_qty = $parent.find('input[name="add_qty"]');
                qty = combination.virtual_available || 1;
                $input_add_qty.val(qty);
            }
            if (qty > combination.virtual_available
                || combination.virtual_available < 1 || qty < 1) {
                $parent.find('#add_to_cart').addClass('disabled out_of_stock');
                $parent.find('#buy_now').addClass('disabled out_of_stock');
            }
            var stickyMedia = new publicWidget.registry.StickProductMedia();
            stickyMedia._stickyButtonAccessability();
        }

        xml_load.then(function () {
            $('.oe_website_sale')
                .find('.availability_message_' + combination.product_template)
                .remove();

            var $message = $(QWeb.render(
                'website_sale_stock.product_availability',
                combination
            ));
            $('div.availability_messages').html($message);
        });
    }

publicWidget.registry.WebsiteSale.include({

    _onChangeCombination: function (){
        this._super.apply(this, arguments);
        VariantMixin._onChangeCombinationStockCustom.apply(this, arguments);
    }
});

return VariantMixin;
});
