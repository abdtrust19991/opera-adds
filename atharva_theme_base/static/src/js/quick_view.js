odoo.define('atharva_theme_base.product_quick_veiw', function(require){
"use strict";
require("web.dom_ready");
var publicWidget = require("web.public.widget");
var core = require("web.core");
var ajax = require("web.ajax");
var rpc = require("web.rpc");
var _t = core._t;
publicWidget.registry.quick_view = publicWidget.Widget.extend({
    "selector":"#wrapwrap",
    events : {
        "click a.o_quick_view": "_quickViewLoad"
    },
    _quickViewLoad:function(evt){
        var pid = $(evt.currentTarget).attr("data-product_template_id");
        ajax.jsonRpc("/get_prod_quick_view_details", "call", {"prod_id":pid}).then(function(data)
        {
            var sale = new publicWidget.registry.WebsiteSale();
            $(".quick_cover").append(data);
            $(".quick-cover-overlay").fadeIn();
            sale.init();
            $(".quick_cover").css("display", "block");
            $("[data-attribute_exclusions]").on("change", function(event) {
                sale.onChangeVariant(event);
            });
            $("[data-attribute_exclusions]").trigger("change");
            $(".css_attribute_color input").click(function(event){
                sale._changeColorAttribute(event);
            });
            // Add to cart from Quick View
            $(".a-submit").on("click", function(event) {
                sale._onClickAdd(event);
            });
            // Add Quantity from Quick View
            $("a.js_add_cart_json").on("click", function(event) {
                sale._onClickAddCartJSON(event);
            });
            // Change Quantity from Quick View
            $("input[name='add_qty']").on("change", function(event) {
                sale._onChangeAddQuantity(event);
            });
            // Close Quick View
            $(".qv_close").click(function() {
                $(".quick_cover").empty(data);
                $(".zoomContainer").remove();
            });
        });
    }
});
});
