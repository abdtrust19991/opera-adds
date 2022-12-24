odoo.define("theme_alan.product", function(require) {
"use strict";

const publicWidget = require("web.public.widget");

publicWidget.registry.product = publicWidget.Widget.extend({
    selector: "#wrapwrap",
    'events':{
        'click a.img-gallery-tag':'_productImageClick',
        'click a.video-gallery-tag':'_productVideoClick',
        'click div.slick-active':'_onClickThumbImg',
        'click a.carousel-control-next':'_changeNxtImg',
        'click a.carousel-control-prev':'_changePreImg',
    },
    start: function() {
        self = this;
        this._super.apply(this, arguments);
        self.displayHeader();
    },
    _changePreImg:function(ev){
        ev.preventDefault();
        var $getActiveElm = this.$el.find('.thumb-active');
        var thumbIndex = this.$el.find('.thumb-active').parent().parent().attr('data-slick-index');
        var ProdCurrIndex = this.$el.find('.carousel-item.h-100.active').index();
        ProdCurrIndex = ProdCurrIndex - 1;
        thumbIndex = parseInt(thumbIndex) - 1;
        var totalImg = $("#thumbs-sliders").attr('data-total_img');
        var isVertical = $("[data-vertical='True']").length;
        var isHorizontal = $("[data-horizontal='True']").length;
        if(parseInt(totalImg) < 6 && isVertical == 1){
            if(ProdCurrIndex == 0){
                var createElem = "[data-slick-index="+totalImg +"]";
                $(createElem).children().children().addClass('thumb-active');
            }
        }
        else if(parseInt(totalImg) < 7 && isHorizontal == 1){
            if(ProdCurrIndex == 0){
                var createElem = "[data-slick-index="+totalImg +"]";
                $(createElem).children().children().addClass('thumb-active');
            }
        }
        if(ProdCurrIndex === -1 && thumbIndex === -1){
            $getActiveElm.removeClass('thumb-active');
            var getNumImg = $("#thumbs-sliders").attr('data-total_img');
            getNumImg = parseInt(getNumImg);
            if(isVertical == true){
                var jumpLastSlider = getNumImg - 5;
            }else{
                var jumpLastSlider = getNumImg - 6;
            }
            var lastImgIndex = getNumImg - 1;
            var createElem = "[data-slick-index="+ lastImgIndex +"]";
            $(createElem).children().children().addClass('thumb-active');
            $('.thumbnails-slides').slick('slickGoTo',jumpLastSlider);
        }
        else{
            if(ProdCurrIndex === thumbIndex){
                var getCurIdn = $getActiveElm.parent().parent().prev().attr('data-slick-index');
                if(isVertical == 1){
                    var maxSlider = totalImg - 5;
                    if(getCurIdn >= maxSlider ){
                        $('.thumbnails-slides').slick('slickGoTo',maxSlider);
                    }
                    else{
                        $('.thumbnails-slides').slick('slickGoTo',getCurIdn);
                    }
                }else{
                    var maxSlider = totalImg - 6;
                    if(getCurIdn >= maxSlider ){
                        $('.thumbnails-slides').slick('slickGoTo',maxSlider);
                    }
                    else{
                        $('.thumbnails-slides').slick('slickGoTo',getCurIdn);
                    }
                }
                $getActiveElm.removeClass('thumb-active').parent().parent().prev().children().children().addClass('thumb-active');

            }

        };
    },
    _changeNxtImg:function(ev){
        ev.preventDefault();
        var $getActiveElm = this.$el.find('.thumb-active');
        var thumbIndex = this.$el.find('.thumb-active').parent().parent().attr('data-slick-index');
        var ProdCurrIndex = this.$el.find('.carousel-item.h-100.active').index();
        var totalImg = $("#thumbs-sliders").attr('data-total_img');
        var totalImg = $("#thumbs-sliders").attr('data-total_img');
        var isVertical = $("[data-vertical='True']").length;
        var isHorizontal = $("[data-horizontal='True']").length;
        totalImg = totalImg - 1;
        if(parseInt(totalImg) < 6 && isVertical == 1){
            if(ProdCurrIndex == totalImg){
                $("[data-slick-index='0']").children().children().addClass('thumb-active');
            }
        }
        else if(parseInt(totalImg) < 7 && isHorizontal == 1){
            if(ProdCurrIndex == totalImg){
                $("[data-slick-index='0']").children().children().addClass('thumb-active');
            }
        }

        if(ProdCurrIndex === parseInt(totalImg)){
            $getActiveElm.removeClass('thumb-active');
            $("[data-slick-index=0]").children().children().addClass('thumb-active');
            $('.thumbnails-slides').slick('slickGoTo',0);
        }else{
            if(ProdCurrIndex === parseInt(thumbIndex)){
                var getCurIdn = $getActiveElm.parent().parent().next().attr('data-slick-index')
                if(isVertical == 1){
                    var maxSlider = totalImg - 4;
                    if(getCurIdn >= maxSlider ){
                        $('.thumbnails-slides').slick('slickGoTo',maxSlider);
                    }
                    else{
                        $('.thumbnails-slides').slick('slickGoTo',getCurIdn);
                    }
                }else{
                    var maxSlider = totalImg - 5;
                    if(getCurIdn >= maxSlider ){
                        $('.thumbnails-slides').slick('slickGoTo',maxSlider);
                    }
                    else{
                        $('.thumbnails-slides').slick('slickGoTo',getCurIdn);
                    }
                }
                $getActiveElm.removeClass('thumb-active').parent().parent().next().children().children().addClass('thumb-active');
            }
        }
    },
    _onClickThumbImg:function(e){
        this.$el.find('.thumb-active').removeClass('thumb-active');
        $(e.currentTarget).children().children().addClass('thumb-active');
    },
    _productImageClick:function(e){
        e.preventDefault();
        $(e.currentTarget).parent().parent().magnificPopup({
            delegate: 'a',
            type: 'image',
            gallery: {
                enabled: true,
            }
        })
    },
    _productVideoClick:function(e){
        e.preventDefault();
        $(e.currentTarget).parent().magnificPopup({
            delegate: 'a',
            disableOn: 700,
            type: 'iframe',
            mainClass: 'mfp-fade',
            removalDelay: 160,
            preloader: false,
            fixedContentPos: false
        });
    },

    displayHeader: function() {
        $("#wrapwrap").on("scroll", function() {
            const getPriceHtml = $("div#product_details .product_price").html();
            if ($(".as_prod_sticky").length && $("div#product_details a#add_to_cart").length) {
                if ($(this).scrollTop() > $("div#product_details a#add_to_cart").offset().top) {
                    $("div#wrapwrap .as_prod_sticky").fadeIn();
                    /* Prices on AddtoCart sticky*/
                    if ($(".js_product .js_main_product").hasClass("css_not_available")) {
                        $("div#wrapwrap .prod_price").html("");
                        $(".as_prod_sticky .as_add_cart #add_to_cart, .as_prod_sticky .as_add_cart #buy_now").addClass("disabled");
                    } else {
                        $("div#wrapwrap .prod_price").html(getPriceHtml);
                        $(".as_prod_sticky .as_add_cart #add_to_cart, .as_prod_sticky .as_add_cart #buy_now").removeClass("disabled");
                    }

                    $(".as_prod_sticky .as_add_cart #add_to_cart").click(function() {
                        $("div#product_details .js_product .js_main_product #add_to_cart").trigger("click");
                    });
                    $(".as_prod_sticky .as_add_cart #buy_now").click(function() {
                        $("div#product_details .js_product .js_main_product #buy_now").trigger("click");
                    });
                } else {
                    $("div#wrapwrap .as_prod_sticky").fadeOut();
                }
            }
        });
    },
});
});