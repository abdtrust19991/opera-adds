odoo.define("atharva_theme_base.searching_extends", function (require) {
"use strict";

var publicWidget = require('web.public.widget');
var search = require("website_sale.s_products_searchbar")

publicWidget.registry.productsSearchBar.include({
    events: {
        "input .search-query": "_onInput",
        "focusout": "_onFocusOut",
        "keydown .search-query": "_onKeydown",
        "change #selectedCat":"_onInput"
    },
    _fetch: function () {
        return this._rpc({
            route: "/shop/products/autocomplete",
            params: {
                "term": this.$input.val(),
                "options": {
                    "order": this.order,
                    "limit": this.limit,
                    "display_description": this.displayDescription,
                    "display_price": this.displayPrice,
                    "max_nb_chars": Math.round(Math.max(this.autocompleteMinWidth, parseInt(this.$el.width())) * 0.22),
                    "category":$("#selectedCat").val(),
                },
            },
        });
    },
});

publicWidget.registry.selectedCat = publicWidget.Widget.extend({
    "selector":".selected-cat",
    events:{
        "click":"_changeCategory"
    },
    _changeCategory:function(ev){
        var getcatid = $(ev.currentTarget).attr("data-id");
        var getcatname = $(ev.currentTarget).text().trim();
        $("#selectedCat").val(getcatid);
        $("#dropdownCatMenuButton").text(getcatname);
        $(".selected-cat").removeClass("text-primary");
        $(ev.currentTarget).addClass("text-primary");
    }
});
});
