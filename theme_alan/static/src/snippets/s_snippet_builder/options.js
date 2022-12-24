odoo.define('theme_alan.snippet_builder',function(require) {
'use strict';

var core = require('web.core');
var QWeb = core.qweb;
var options = require('web_editor.snippets.options');
var _t = core._t;
var Dialog = require('web.Dialog');

options.registry['js_alan_snippet_builder'] = options.Class.extend({
    xmlDependencies: ['/theme_alan/static/src/xml/alan_snippet_temp/homepage.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/portfolio.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/sliders.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/banner.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/shop_banner.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/about.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/services.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/features.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/price_table.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/our_team.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/our_clients.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/collection.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/contact_us.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/call_to_action.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/promotion.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/parallax.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/afq.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/gallary.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/tabs.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/video_popup.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/category.xml',
                    '/theme_alan/static/src/xml/alan_snippet_temp/testimonial.xml',
                    '/theme_alan/static/src/xml/website_snippet_builder.xml'],
    events:{
        'click':'_changeCollection'
    },
    _changeCollection:function(){
        this.select_snippet('click','true');
    },
    select_snippet: function(type, value) {
        var self = this;
        this.id = this.$target.attr('id');
        var markupStr = this.$target.html();
        if(type == false || type == 'click'){
            var dialog = new Dialog(self, {
                size: 'extra-large',
                title: 'Alan Snippet Builder',
                $content: QWeb.render('theme_alan.builder_block'),
                buttons: [{text: _t('Save'), classes: 'btn-primary', close: true, click: function () {
                    var snippet = $("input[name='radio-snippet']:checked").closest('.snippet-as').find('textarea').val();
                    var data = self.$target.empty().append(snippet);
                    var model = self.$target.parent().attr('data-oe-model');
                    if(model){
                        self.$target.parent().addClass('o_editable o_dirty');
                    }
                }}, {text: _t('Discard'), close: true}],
            });
            dialog.open();
            return self;
        }
    },
    onBuilt: function () {
        var self = this;
        this._super();
        this.select_snippet('click', 'true');
    },
});

$(document).on('click', '.edit-snippet-builder-box .e-sb-tab label', function(){
    $('.edit-snippet-builder-box .e-sb-tab label').removeClass('e-sb-active');
    $(this).addClass('e-sb-active');
    var tagid = $(this).data('tag');
    $('.e-sb-tab--content').removeClass('active').addClass('d-none');
    $('#'+tagid).addClass('active').removeClass('d-none');
});
});
