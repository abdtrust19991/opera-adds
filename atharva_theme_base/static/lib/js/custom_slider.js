odoo.define('atharva_theme_base.custom_slider', function(require){
'use strict';

    $(document).ready(function() {
        $('#as_accessory_product').owlCarousel({
            items: 3,
            margin: 10,
            dots:false,
            nav: true,
            navText : ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
            responsive: {
                0: {
                    items: 2,
                },
                768: {
                    items: 3,
                }

            }
        });
        $('#as_alternative').owlCarousel({
            items: 3,
            margin: 10,
            dots:false,
            nav: true,
            navText : ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
            responsive: {
                0: {
                    items: 2,
                },
                768: {
                    items: 3,
                }

            }
        });

    });

    // Mega Category Level Menu
    $(document).on('mouseenter', 'header li.mm-mega-menu', function() {
        if ($(this).find(".mm-maga-main.mm-mega-cat-level").length > 0) {
            var $first_tab = $(this).find(".mm-category-level .mm-cat-level-1:eq(0)");
            $first_tab.find(".cat-level-title").addClass("active-li");
            $first_tab.find(".mm-cat-level-2").addClass("menu-active");
        }
    });

    $(document).on('mouseenter', '.mm-cat-level-1', function() {
        var $first_div = $(this).find('.cat-level-title');
        $first_div.addClass("active-li");
        $(this).find('.mm-cat-level-2').addClass("menu-active");
    });

    $(document).on('mouseleave', '.mm-cat-level-1', function() {
        var $first_div = $(this).find('.cat-level-title')
        $first_div.removeClass("active-li");
        $(this).find('.mm-cat-level-2').removeClass("menu-active");
    });

});