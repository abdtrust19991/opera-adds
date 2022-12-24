odoo.define('atharva_theme_base.megamenu_extends', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var wUtils = require('website.utils');
var dom = require('web.dom');
var menu = require('website.content.menu')

publicWidget.registry.autohideMenu.include({
    async start() {
    this.$topMenu = this.$('#top_menu');
    if (this.$topMenu.length && this.$topMenu.find('.mm-mega-menu').length){
        this.noAutohide = this.$el.is('.o_no_autohide_menu');
        if (!this.noAutohide) {
            await wUtils.onceAllImagesLoaded(this.$('.navbar'),
                this.$('.o_mega_menu, .o_offcanvas_logo_container, .dropdown-menu .o_lang_flag, .mm-mega-menu'));
            var $window = $(window);
            $window.on('load.autohideMenu', function () {
                $window.trigger('resize');
            });
            dom.initAutoMoreMenu(this.$topMenu, {unfoldable: '.divider, .divider ~ li'});
        }
        this.$topMenu.removeClass('o_menu_loading');
        this.$topMenu.trigger('menu_loaded');
        return Promise.resolve();
    }
    else{
        await this._super(...arguments);
    }
    },
});
});
