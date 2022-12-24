odoo.define("atharva_theme_base.quick_load_product", function (require) {
"use strict";

var publicWidget = require("web.public.widget");
var url = window.location.href;

publicWidget.registry.ajaxProductLoad = publicWidget.Widget.extend({
    "selector": ".js_load_product",
    events : {
        "click": "_loadProduct"
    },
    _loadProduct:function(){
        var checkaction = this.$el.attr("id");
        var page = this.$el.attr("page");
        if(checkaction == "nxt"){
            this._rpc({
                route: "/json/shop/product/",
                params: {
                    "page":this.$el.attr("page"),
                    "category_id":this.$el.attr("category"),
                    "ppg":this.$el.attr("ppg"),
                    "attrval":this.$el.attr("attrval"),
                    "attrib":this.$el.attr("attrib"),
                    "brand":this.$el.attr("brand"),
                    "min_val":this.$el.attr("min_val"),
                    "max_val":this.$el.attr("max_val"),
                    "brand_ids":this.$el.attr("brand_ids"),
                    "order":this.$el.attr("product_order"),
                    "search":this.$el.attr("search"),
                    "rating":this.$el.attr("rating"),
                    "tag_val":this.$el.attr("tag_val"),
                }
            }).then(function (result) {
                $(".load_next_product").before(result["product"]);
                $(".pagination").replaceWith(result["pager_template"]);
            });
            var maxpage = this.$el.attr("max_page");
            var page = Number(page) + 1;
            this.$el.attr("page",page);
            if(page == maxpage){this.$el.remove();}
        }
        else{
            this._rpc({
                route: "/json/shop/product/",
                params: {
                    "page":this.$el.attr("page"),
                    "category_id":this.$el.attr("category"),
                    "ppg":this.$el.attr("ppg"),
                    "attrval":this.$el.attr("attrval"),
                    "attrib":this.$el.attr("attrib"),
                    "brand":this.$el.attr("brand"),
                    "min_val":this.$el.attr("min_val"),
                    "max_val":this.$el.attr("max_val"),
                    "brand_ids":this.$el.attr("brand_ids"),
                    "order":this.$el.attr("product_order"),
                    "search":this.$el.attr("search"),
                    "rating":this.$el.attr("rating"),
                    "tag_val":this.$el.attr("tag_val"),
                    "previous":true,
                }
            }).then(function (result) {
                $(".load_pre_product").after(result["product"]);
                $(".pagination").replaceWith(result["pager_template"]);
            });
            var page = Number(page) - 1;
            this.$el.attr("page",page);
            if(page == 1){this.$el.remove();}
        }
        var checkurl = url.split("/");
        var checkattrurl = url.split("=");
        var url_have_page = false;
        if(checkattrurl.length > 1){
            var spliturl = url.split("?");
            var checksuburl = spliturl[0].split("/");
            for (let index = 0; index < checksuburl.length; index++){
                if(checksuburl[index] == "page"){
                    url_have_page = true;
                }
            }
            if(url_have_page != true){
                var new_url =  checksuburl.join("/") + "/page/" + page + "?" +spliturl[1];
            }else{
                checksuburl.pop();
                checksuburl.push(page);
                var new_url = checksuburl.join("/") + "?" +spliturl[1];
            }
        }else{
            for (let index = 0; index < checkurl.length; index++) {
                if(checkurl[index] == "page"){
                    url_have_page = true;
                }
            }
            if(url_have_page != true){
                var new_url = url + "/page/" + page;
            }else{
                checkurl.pop();
                checkurl.push(page);
                var new_url = checkurl.join("/");
                }
            }
        $(".page-item").each(function () {
            var getclassid = $(this).attr("id");
            if(getclassid != undefined){
                var getpagenum = getclassid.slice(4);
                var activediv = $(this).hasClass("active");
                if(activediv == true){
                    $(this).removeClass("active");
                }
                if(getpagenum == page){
                    $(this).addClass("active");
                }
            }
        });
            window.history.pushState("data","Title",new_url);
        },
    });
});
