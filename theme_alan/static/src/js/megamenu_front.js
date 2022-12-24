odoo.define("theme_alan.megamenu_front_js", function (require) {
"use strict";

var publicWidget = require("web.public.widget");

publicWidget.registry.megemenu_multi_leve = publicWidget.Widget.extend({
    "selector":"#wrapwrap",
    events:{
        "mouseenter header li.mm-mega-menu": "_active_mm",
        "mouseenter .mm-cat-level-1":"_active_menu",
        "mouseleave .mm-cat-level-1":"_inactive_menu",
    },
    _active_mm:function(evt){
        if ($(evt.currentTarget).find(".mm-maga-main.mm-mega-cat-level").length > 0) {
            var $first_tab = $(evt.currentTarget).find(".mm-category-level .mm-cat-level-1:eq(0)");
            $first_tab.find(".cat-level-title").addClass("active-li");
            $first_tab.find(".mm-cat-level-2").addClass("menu-active");
        }
    },
    _active_menu:function(evt){
        var $first_div = $(evt.currentTarget).find(".cat-level-title");
        $first_div.addClass("active-li");
        $(evt.currentTarget).find(".mm-cat-level-2").addClass("menu-active");
    },
    _inactive_menu:function(evt){
        var $first_div = $(evt.currentTarget).find(".cat-level-title")
        $first_div.removeClass("active-li");
        $(evt.currentTarget).find(".mm-cat-level-2").removeClass("menu-active");
    }
});
});
