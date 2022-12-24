odoo.define('opera_pos_order_return_and_reprint.pos_return', function(require) {
"use strict";


    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
        var chrome = require('point_of_sale.chrome');
        var NumpadWidget = screens.NumpadWidget;

    var utils = require('web.utils');
    var round_pr = utils.round_precision;
var round_di = utils.round_decimals;
var field_utils = require('web.field_utils');

    var _t = core._t;

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({


        push_order: function(order, opts){
            var self = this;
            var pushed = _super_posmodel.push_order.call(this, order, opts);
            return pushed;
        },



//        load_new_partners: function(){
//            var self = this;
//            var def  = new $.Deferred();
//            var fields = _.find(this.models,function(model){ return model.model === 'res.partner'; }).fields;
////            var domain = [['customer','=',true],['write_date','>',this.db.get_partner_write_date()],['user_id','=',this.user.id]];
//            var domain = [['customer','=',true],['write_date','>',this.db.get_partner_write_date()]];
//            rpc.query({
//                    model: 'res.partner',
//                    method: 'search_read',
//                    args: [domain, fields],
//                }, {
//                    timeout: 3000,
//                    shadow: true,
//                })
//                .then(function(partners){
//                    if (self.db.add_partners(partners)) {   // check if the partners we got were real updates
//                        def.resolve();
//                    } else {
//                        def.reject();
//                    }
//                }, function(type,err){ def.reject(); });
//            return def;
//        },

        _save_to_server: function(orders, options) {
            var self = this;
            return _super_posmodel._save_to_server.call(this, orders, options).then(function(new_orders) {
                if (new_orders != null) {
                    new_orders.forEach(function(order) {
                        if (order) {

                            //new Model('pos.order').call('return_new_order', [order])
                            rpc.query({
		                        model: 'pos.order',
		                        method: 'return_new_order',
		                        args: [order.id],

		                        }).then(function(output) {
		                            self.db.all_orders_list.unshift(output);
		                            self.db.get_orders_by_id[output.id] = output;
		                    });
		                    //######################################################################################

		                    rpc.query({
		                        model: 'pos.order',
		                        method: 'return_new_order_line',
		                        args: [order.id],

		                        }).then(function(output1) {
		                            for(var ln=0; ln < output1.length; ln++){
		                                self.db.all_orders_line_list.unshift(output1[ln]);
		                                self.db.get_lines_by_id[output1[ln].id] = output1[ln];
		                            }
		                    });


		                    //######################################################################################

		                    rpc.query({
		                        model: 'pos.order',
		                        method: 'new_pack_lot_lines',
		                        args: [order.id],

		                        }).then(function(output1) {
		                            for(var ln=0; ln < output1.length; ln++){
		                                self.db.all_lot_lines_list.unshift(output1[ln]);
		                                 self.db.get_lot_lines_by_id[output1[ln].id] = output1[ln];

		                            }
		                             });


                        }
                    });
                }
                return new_orders;
            });
        }
    });


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            if (this.barcode) {
                json.barcode = this.barcode;
            }
            if (!this.barcode && this.uid) { // init barcode and automatic create barcode for order
                var barcode = '9';
                var uid = this.uid;
                uid = uid.substring(1);
                var fbarcode = uid.split('-');
                for (var i in fbarcode) {
                    barcode += fbarcode[i];
                }

                var min =11111;
                var max = 99999;
                var rand = Math.floor(Math.random() * (max - min + 1)) + min;
                barcode +=rand;


                barcode = barcode.split("");
                var abarcode = []
                var sbarcode = ""
                for (var i = 0; i < barcode.length; i++) {
                    if (i < 12) {
                        sbarcode += barcode[i]
                        abarcode.push(barcode[i])
                    }
                }
                this.barcode = sbarcode + this.generate_barcode(abarcode).toString()
            }
//            console.log('export json');
//            console.log(json);
            return json;
        },
        generate_barcode: function (code) {
            if (code.length != 12) {
                return -1
            }
            var evensum = 0;
            var oddsum = 0;
            for (var i = 0; i < code.length; i++) {
                if ((i % 2) == 0) {
                    evensum += parseInt(code[i])
                } else {
                    oddsum += parseInt(code[i])
                }
            }
            var total = oddsum * 3 + evensum
            return parseInt((10 - total % 10) % 10)
        },
        init_from_JSON: function (json) {
            var res = _super_order.init_from_JSON.apply(this, arguments);
            if (json.barcode) {
                this.barcode = json.barcode;
            }
            return res;
        },

        get_total_without_discount_tax: function(){
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                if(orderLine.get_unit_price() > 0){
                    return sum + orderLine.get_price_without_discount();
                }
                else{
                    return sum
                }
            }), 0), this.pos.currency.rounding);
        },

        get_global_discount_product:function(){
            var lines = this.get_orderlines();
            for (var i = 0; i < lines.length; i++) {
                if(lines[i].price_unit < 0)
                {
                    var product = lines[i].get_product();
                    return lines[i];
                }
            }
            return null;

        },




    });

// Load Models here...
function get_my_date(dateOffset){
//    var dateOffset = 30 ;
    var myDate = new Date();
    myDate.setDate(myDate.getDate() - dateOffset);
    myDate.setHours(0);
    myDate.setMinutes(0);
    myDate.setSeconds(0);
    return myDate;
}


    models.load_models({
        model: 'pos.order',
        fields: ['name', 'id', 'date_order', 'partner_id', 'pos_reference', 'lines', 'amount_total', 'session_id',
                    'state', 'company_id','barcode'],
        domain: function(self){ return [['date_order','>=',get_my_date(self.config.return_order_duration)],['amount_total','>',0.0],['state', 'not in', ['draft', 'cancel']]]; },
        loaded: function(self, orders){
        	self.db.all_orders_list = [];

        	self.db.get_orders_by_id = {};
        	self.orders = [];
            orders.forEach(function(order) {
                var order_date = new Date(order.date_order);
                var myDate = get_my_date(self.config.return_order_duration);
                if(order.amount_total > 0.0 && order_date > myDate){
                        var order_date_local = moment(order_date).add(2, 'hours');
                        order.date_order = moment(order_date_local).format('YYYY-MM-DD HH:mm:ss');
                        self.db.get_orders_by_id[order.id] = order;
                        self.orders.push(order);
                        self.db.all_orders_list.push(order);
                    }
            });
//            self.orders = orders;
        },
    });

    models.load_models({
        model: 'pos.order.line',
        fields: ['order_id', 'product_id', 'discount', 'qty', 'price_unit','pack_lot_ids','return_line_ids','order_line_id','return_qty'],
        domain: function(self) {
            var order_lines = []
            var orders = self.db.all_orders_list;
            for (var i = 0; i < orders.length; i++) {
                order_lines = order_lines.concat(orders[i]['lines']);
            }
            return [
                ['id', 'in', order_lines]
            ];
        },
        loaded: function(self, pos_order_line) {
            self.db.all_orders_line_list = pos_order_line;
            self.db.get_lines_by_id = {};
            pos_order_line.forEach(function(line) {
                self.db.get_lines_by_id[line.id] = line;
            });

            self.pos_order_line = pos_order_line;
        },
        export_as_JSON: function() {
            var pack_lot_ids = [];
            if (this.has_product_lot){
                this.pack_lot_lines.each(_.bind( function(item) {
                    return pack_lot_ids.push([0, 0, item.export_as_JSON()]);
                }, this));
            }
            var return_line_id = null;
            if (this.original_line_id){
                return_line_id = this.original_line_id;
            }
            json_return = {
                qty: this.get_quantity(),
                price_unit: this.get_unit_price(),
                discount: this.get_discount(),
                product_id: this.get_product().id,
                tax_ids: [[6, false, _.map(this.get_applicable_taxes(), function(tax){ return tax.id; })]],
                id: this.id,
                pack_lot_ids: pack_lot_ids,
                order_line_id: return_line_id,
            }
            if (this.return_qty){
                json_return.return_qty = this.return_qty;
            }
            return json_return;
        },
    });

// lot

    models.load_models({
        model: 'pos.pack.operation.lot',
        fields: ['pos_order_line_id', 'lot_name',],
        domain: function(self) {
            var lot_lines = []
            var order_lines = self.db.all_orders_line_list;
            for (var i = 0; i < order_lines.length; i++) {
                lot_lines = lot_lines.concat(order_lines[i]['pack_lot_ids']);
            }
            return [
                ['id', 'in', lot_lines]
            ];
        },
        loaded: function(self, lot_lines) {
//            self.db.all_orders_line_list = pos_order_line;
//            self.db.get_lines_by_id = {};
//            pos_order_line.forEach(function(line) {
//                self.db.get_lines_by_id[line.id] = line;
//            });
//
//            self.pos_order_line = pos_order_line;

            self.db.all_lot_lines_list = lot_lines;
            self.db.get_lot_lines_by_id = {};
            lot_lines.forEach(function(line) {
                self.db.get_lot_lines_by_id[line.id] = line;
            });

            self.lot_lines = lot_lines;

        },
    });


// end lot


    // exports.Orderline = Backbone.Model.extend ...
    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({


    export_as_JSON: function() {
        var pack_lot_ids = [];
        if (this.has_product_lot){
            this.pack_lot_lines.each(_.bind( function(item) {
                return pack_lot_ids.push([0, 0, item.export_as_JSON()]);
            }, this));
        }
        var return_line_id = null;
        if (this.original_line_id){
            return_line_id = this.original_line_id;
        }
        return {
            qty: this.get_quantity(),
            price_unit: this.get_unit_price(),
            price_subtotal: this.get_price_without_tax(),
            price_subtotal_incl: this.get_price_with_tax(),
            discount: this.get_discount(),
            product_id: this.get_product().id,
            tax_ids: [[6, false, _.map(this.get_applicable_taxes(), function(tax){ return tax.id; })]],
            id: this.id,
            order_line_id: return_line_id,
            pack_lot_ids: pack_lot_ids
        };
    },


    get_price_without_discount:    function(){
        var rounding = this.pos.currency.rounding;
        return round_pr(this.get_unit_price() * this.get_quantity() , rounding);
    },


    });
//    // End Orderline start

    // Start POSBarcodeReturnWidget

    var POSBarcodeReturnWidget = screens.ActionButtonWidget.extend({
        template: 'POSBarcodeReturnWidget',

        button_click: function() {
            var self = this;
//            this.gui.show_popup('pos_barcode_popup_widget', {});
            if (self.pos.config.allow_return_password == true) {
            self.gui.show_popup('passwordinput', {
                'title': _t('Password ?'),
                 confirm: function (pw) {
                    if (pw !== self.pos.config.return_order_password) {
                        self.gui.show_popup('error', {
                            'title': _t('Error'),
                            'body': _t('Incorrect password. Please try again'),
                        });
                    } else {
                        return self.gui.show_popup('pos_barcode_popup_widget', {});
                    }
                    },
                });
            } else {
                return self.gui.show_popup('pos_barcode_popup_widget', {});
            }
        },

    });

    screens.define_action_button({
        'name': 'POS Return Order with Barcode',
        'widget': POSBarcodeReturnWidget,
        'condition': function() {
            return true;
        },
    });
    // End POSBarcodeReturnWidget

	 // ReceiptScreenWidgetNew start
	 var ReceiptScreenWidgetNew = screens.ScreenWidget.extend({
       template: 'ReceiptScreenWidgetNew',
        show: function() {
            var self = this;
            self._super();


            $('.button.back').on("click", function() {
                self.gui.show_screen('see_all_orders_screen_widget');
            });
            $('.button.print').click(function() {
                var test = self.chrome.screens.receipt;
                setTimeout(function() { self.chrome.screens.receipt.lock_screen(false); }, 1000);
                if (!test['_locked']) {
                    self.chrome.screens.receipt.print_web();
                    self.chrome.screens.receipt.lock_screen(true);
                }
            });
        }
    });
    gui.define_screen({ name: 'ReceiptScreenWidgetNew', widget: ReceiptScreenWidgetNew });



    // SeeAllOrdersScreenWidget start

    var SeeAllOrdersScreenWidget = screens.ScreenWidget.extend({
        template: 'SeeAllOrdersScreenWidget',
        init: function(parent, options) {
            this._super(parent, options);
            //this.options = {};
        },

        line_selects: function(event,$line,id){
        	var self = this;
            var orders = this.pos.db.get_orders_by_id[id];
            this.$('.client-list .lowlight').removeClass('lowlight');
            if ( $line.hasClass('highlight') ){
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                //this.display_orders_detail('hide',orders);
                //this.new_clients = null;
                //this.toggle_save_button();
            }else{
                this.$('.client-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                var y = event.pageY - $line.parent().offset().top;
                this.display_orders_detail('show',orders,y);
                //this.new_clients = orders;
                //this.toggle_save_button();
            }

        },

        display_orders_detail: function(visibility,order,clickpos){
            var self = this;
            var contents = this.$('.client-details-contents');
            var parent   = this.$('.orders-line ').parent();
            var scroll   = parent.scrollTop();
            var height   = contents.height();

            contents.off('click','.button.edit');
            contents.off('click','.button.save');
            contents.off('click','.button.undo');

            contents.on('click','.button.save',function(){ self.save_client_details(order); });
            contents.on('click','.button.undo',function(){ self.undo_client_details(order); });


            this.editing_client = false;
            this.uploaded_picture = null;

            if(visibility === 'show'){
                contents.empty();


                //Custom Code for passing the orderlines
                var orderline = [];
                for (var z = 0; z < order.lines.length; z++){
                    orderline.push(self.pos.db.get_lines_by_id[order.lines[z]])
                }
                //Custom code ends

                contents.append($(QWeb.render('OrderDetails',{widget:this,order:order,orderline:orderline})));

                var new_height   = contents.height();

                if(!this.details_visible){
                    if(clickpos < scroll + new_height + 20 ){
                        parent.scrollTop( clickpos - 20 );
                    }else{
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                }else{
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }

                this.details_visible = true;
                //this.toggle_save_button();
             }

             else if (visibility === 'edit') {
            // Connect the keyboard to the edited field
            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                contents.off('click', '.detail');
                searchbox.off('click');
                contents.on('click', '.detail', function(ev){
                    self.chrome.widget.keyboard.connect(ev.target);
                    self.chrome.widget.keyboard.show();
                });
                searchbox.on('click', function() {
                    self.chrome.widget.keyboard.connect($(this));
                });
            }

            this.editing_client = true;
            contents.empty();
            contents.append($(QWeb.render('ClientDetailsEdit',{widget:this})));
            //this.toggle_save_button();

            // Browsers attempt to scroll invisible input elements
            // into view (eg. when hidden behind keyboard). They don't
            // seem to take into account that some elements are not
            // scrollable.
            contents.find('input').blur(function() {
                setTimeout(function() {
                    self.$('.window').scrollTop(0);
                }, 0);
            });

            contents.find('.image-uploader').on('change',function(event){
                self.load_image_file(event.target.files[0],function(res){
                    if (res) {
                        contents.find('.client-picture img, .client-picture .fa').remove();
                        contents.find('.client-picture').append("<img src='"+res+"'>");
                        contents.find('.detail.picture').remove();
                        self.uploaded_picture = res;
                    }
                });
            });
            }



             else if (visibility === 'hide') {
                contents.empty();
                if( height > scroll ){
                    contents.css({height:height+'px'});
                    contents.animate({height:0},400,function(){
                        contents.css({height:''});
                    });
                }else{
                    parent.scrollTop( parent.scrollTop() - height);
                }
                this.details_visible = false;
                //this.toggle_save_button();
            }
        },

        get_selected_partner: function() {
            var self = this;
            if (self.gui)
                return self.gui.get_current_screen_param('selected_partner_id');
            else
                return undefined;
        },

        render_list_orders: function(orders, search_input){
//            New change filter only non return orders
            orders = orders.filter(function (order){
                return (order.amount_total >= 0.0)   ;
            })
            var self = this;
            var selected_partner_id = this.get_selected_partner();
            var selected_client_orders = [];
            if (selected_partner_id != undefined) {
                for (var i = 0; i < orders.length; i++) {
                    if (orders[i].partner_id[0] == selected_partner_id)
                        selected_client_orders = selected_client_orders.concat(orders[i]);
                }
                orders = selected_client_orders;
            }

           if (search_input != undefined && search_input != '') {
                var selected_search_orders = [];
                var search_text = search_input.toLowerCase()
                for (var i = 0; i < orders.length; i++) {
                    if (orders[i].partner_id == '') {
                        orders[i].partner_id = [0, '-'];
                    }
//                    if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].pos_reference.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
//                        selected_search_orders = selected_search_orders.concat(orders[i]);
//                    }
                    if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].pos_reference.toLowerCase()).indexOf(search_text) != -1) ) {
                        selected_search_orders = selected_search_orders.concat(orders[i]);
                    }
                }
                orders = selected_search_orders;
            }


            var content = this.$el[0].querySelector('.orders-list-contents');
	        content.innerHTML = "";
	        var orders = orders;
            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                var order    = orders[i];
                var ordersline_html = QWeb.render('OrdersLine',{widget: this, order:orders[i], selected_partner_id: orders[i].partner_id[0]});
                var ordersline = document.createElement('tbody');
                ordersline.innerHTML = ordersline_html;
                ordersline = ordersline.childNodes[1];
                content.appendChild(ordersline);

            }
        },

        save_client_details: function(partner) {
            var self = this;

            var fields = {};
            this.$('.client-details-contents .detail').each(function(idx,el){
                fields[el.name] = el.value || false;
            });

            if (!fields.name) {
                this.gui.show_popup('error',_t('A Customer Name Is Required'));
                return;
            }

            if (this.uploaded_picture) {
                fields.image = this.uploaded_picture;
            }

            fields.id           = partner.id || false;
            fields.country_id   = fields.country_id || false;

            //new Model('res.partner').call('create_from_ui',[fields])
            rpc.query({
                model: 'res.partner',
                method: 'create_from_ui',
                args: [fields],

                }).then(function(partner_id){
                self.saved_client_details(partner_id);
            },function(err,event){
                event.preventDefault();
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Save Changes'),
                    'body': _t('Your Internet connection is probably down.'),
                });
            });
        },

        undo_client_details: function(partner) {
            this.display_orders_detail('hide');

        },

        saved_client_details: function(partner_id){
            var self = this;
            self.display_orders_detail('hide');
            alert('!! Customer Created Successfully !!')

        },

        show_return_order_popup: function(order_id){
            var self = this;
            var orderlines = [];
            var orders = this.pos.db.all_orders_list;
            var order_line_data = this.pos.db.all_orders_line_list;
            var selectedOrder = null;
//            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
//                if (orders[i] && orders[i].id == order_id) {
//                    selectedOrder = orders[i];
//                }
//            }
            selectedOrder = self.pos.db.get_orders_by_id[order_id];
            selectedOrder.lines.forEach(function(line_id) {

                for(var y=0; y<order_line_data.length; y++){
                    if(order_line_data[y]['id'] == line_id && order_line_data[y]['price_unit'] > 0.0 ){
                        var product_id = order_line_data[y].product_id[0];
                        var product = self.pos.db.get_product_by_id(product_id);
//                        if(!product.is_delivery){
                            orderlines.push(order_line_data[y]);
//                        }

                    }
                }
           });

            this.gui.show_popup('pos_return_order_popup_widget', { 'orderlines': orderlines, 'order': selectedOrder });

        },

        show: function(options) {
            var self = this;
            this._super(options);

            this.details_visible = false;

            var orders = self.pos.db.all_orders_list;
            var orders_lines = self.pos.db.all_orders_line_list;
            this.render_list_orders(orders, undefined);

	    	this.$('.back').click(function(){
		        self.gui.show_screen('products');
            });

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-name', 'click', function(event) {

               for(var ord = 0; ord < orders.length; ord++){
                   if (orders[ord]['id'] == $(this).data('id')){
                    var orders1 = orders[ord];
                   }
               }

               var orderline = [];
               for(var n=0; n < orders_lines.length; n++){
                   if (orders_lines[n]['order_id'][0] == $(this).data('id')){
                    orderline.push(orders_lines[n])
                   }
               }

                self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline});

            });

            //################################################################################################################

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-ref', 'click', function(event) {


               for(var ord = 0; ord < orders.length; ord++){
                   if (orders[ord]['id'] == $(this).data('id')){
                    var orders1 = orders[ord];
                   }
               }
                var orderline = [];
                for(var n=0; n < orders_lines.length; n++){
                    if (orders_lines[n]['order_id'][0] == $(this).data('id')){
                     orderline.push(orders_lines[n])
                    }
                }

                self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline});

            });

            //################################################################################################################

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-partner', 'click', function(event) {


               for(var ord = 0; ord < orders.length; ord++){
                   if (orders[ord]['id'] == $(this).data('id')){
                    var orders1 = orders[ord];
                   }
               }


                var orderline = [];
                for(var n=0; n < orders_lines.length; n++){
                    if (orders_lines[n]['order_id'][0] == $(this).data('id')){
                     orderline.push(orders_lines[n])
                    }
                }

                self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline});
           });

            //################################################################################################################

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-date', 'click', function(event) {

               for(var ord = 0; ord < orders.length; ord++){
                   if (orders[ord]['id'] == $(this).data('id')){
                    var orders1 = orders[ord];
                   }
               }

                var orderline = [];
                for(var n=0; n < orders_lines.length; n++){
                    if (orders_lines[n]['order_id'][0] == $(this).data('id')){
                     orderline.push(orders_lines[n])
                    }
                }

                self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline});


               // self.line_selects(event, $(this), parseInt($(this).data('id')));
            });

            //################################################################################################################

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-tot', 'click', function(event) {

               for(var ord = 0; ord < orders.length; ord++){
                   if (orders[ord]['id'] == $(this).data('id')){
                    var orders1 = orders[ord];
                   }
               }

                var orderline = [];
                for(var n=0; n < orders_lines.length; n++){
                    if (orders_lines[n]['order_id'][0] == $(this).data('id')){
                     orderline.push(orders_lines[n])
                    }
                }

                self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline});
            });

            //################################################################################################################


            this.$('.orders-list-contents').delegate('.print-order', 'click', function(result) {
                var order_id = parseInt(this.id);
                var orderlines = [];
		        var paymentlines = [];
		        var discount = 0;
		        var subtotal = 0;
		        var tax = 0;

                var selectedOrder = null;
//		        for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
//		            if (orders[i] && orders[i].id == order_id) {
//		                selectedOrder = orders[i];
//		            }
//		        }
                selectedOrder = self.pos.db.get_orders_by_id[order_id];
		            rpc.query({
				        model: 'pos.order',
				        method: 'print_pos_receipt',
				        args: [order_id],

		            }).then(function(output) {

					orderlines = output[0];
		            paymentlines = output[2];
		            discount = output[1];
//		            subtotal = output[4];
//		            tax = output[5];
		            var sub_total_before_discount = output[4];
		            var global_discount_percent = output[5];
		            self.gui.show_screen('ReceiptScreenWidgetNew');
		            $('.pos-receipt-container').html(QWeb.render('PosTicket1',{
		                widget:self,
		                a2: window.location.origin +  '/web/image?model=pos.config&field=image&id=' + self.pos.config.id,
		                order: selectedOrder,
		                paymentlines: paymentlines,
		                orderlines: orderlines,
		                discount_total: discount,
		                change: output[3],
		                subtotal: subtotal,
		                global_discount_percent: global_discount_percent,
		                sub_total_before_discount: sub_total_before_discount,
		                tax: tax,
		            }));
				});
            });

            //Return Order
            this.$('.orders-list-contents').delegate('.return-order', 'click', function(result) {
                var order_id = parseInt(this.id);
                if (self.pos.config.allow_return_password == true) {
                    self.gui.show_popup('passwordinput', {
                        'title': _t('Password ?'),
                         confirm: function (pw) {
                            if (pw !== self.pos.config.return_order_password) {
                                self.gui.show_popup('error', {
                                    'title': _t('Error'),
                                    'body': _t('Incorrect password. Please try again'),
                                });
                            } else {
                                return self.show_return_order_popup(order_id);
                            }
                            },
                        });
                    } else {
                        return self.show_return_order_popup(order_id);
                    }

            });
            //End Return Order


            this.$('.orders-list-contents').delegate('.re-order', 'click', function(result) {

                var order_id = parseInt(this.id);

                var selectedOrder = null;
//		        for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
//		            if (orders[i] && orders[i].id == order_id) {
//		                selectedOrder = orders[i];
//		            }
//		        }

                selectedOrder = self.pos.db.get_orders_by_id[order_id];

                var orderlines = [];
            	var order_list = self.pos.db.all_orders_list;
                var order_line_data = self.pos.db.all_orders_line_list;

                selectedOrder.lines.forEach(function(line_id) {

		            //###############################################################################
		            for(var y=0; y<order_line_data.length; y++){
		                if(order_line_data[y]['id'] == line_id){
		                   orderlines.push(order_line_data[y]);
		                }
		            }
		            //###############################################################################
                });

            	self.gui.show_popup('pos_re_order_popup_widget', { 'orderlines': orderlines, 'order': selectedOrder });
            });

            //this code is for Search Orders
            this.$('.search-order input').keyup(function() {
                self.render_list_orders(orders, this.value);
            });

            this.$('.new-customer').click(function(){
                self.display_orders_detail('edit',{
                    'country_id': self.pos.company.country_id,
                });
            });
        },
        //


    });
    gui.define_screen({
        name: 'see_all_orders_screen_widget',
        widget: SeeAllOrdersScreenWidget
    });

    // End SeeAllOrdersScreenWidget


    //==================================================================================================

    var SeeOrderDetailsPopupWidget = popups.extend({
        template: 'SeeOrderDetailsPopupWidget',

        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },


        show: function(options) {
        	var self = this;
            options = options || {};
            this._super(options);
            this.order = options.order || [];
            this.orderline = options.orderline || [];
        },
        events: {
            'click .button.cancel': 'click_cancel',
        },
        renderElement: function() {
            var self = this;
            this._super();
        },

    });

    gui.define_popup({
        name: 'see_order_details_popup_widget',
        widget: SeeOrderDetailsPopupWidget
    });

    // PosReOrderPopupWidget Popup start

    var PosReOrderPopupWidget = popups.extend({
        template: 'PosReOrderPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        //
        show: function(options) {
        	options = options || {};
            var self = this;
            this._super(options);
            this.orderlines = options.orderlines || [];

        },
        //
        renderElement: function() {
            var self = this;
            this._super();
            var selectedOrder = this.pos.get_order();
            var orderlines = self.options.orderlines;
            var order = self.options.order;

            // When you click on apply button, Customer is selected automatically in that order
            var partner_id = false
            var client = false
            if (order && order.partner_id != null)
                partner_id = order.partner_id[0];
                client = this.pos.db.get_partner_by_id(partner_id);

			var reorder_products = {};

            this.$('#apply_reorder').click(function() {
                var entered_code = $("#entered_item_qty").val();
                var list_of_qty = $('.entered_item_qty');

				$.each(list_of_qty, function(index, value) {
				 	var entered_item_qty = $(value).find('input');
               	    var qty_id = parseFloat(entered_item_qty.attr('qty-id'));
               	    var return_qty = parseFloat(entered_item_qty.attr('nqty'));
		            var line_id = parseFloat(entered_item_qty.attr('line-id'));
		            var entered_qty = parseFloat(entered_item_qty.val());

		            reorder_products[line_id] = entered_qty;
            	});
            var order = self.options.order;
            console.log('order');
            console.log(order);
            var global_discount = order.get_global_discount_product();
            console.log('global_discount');
            console.log(global_discount);
            if(global_discount){
//            	    console.log("global discount applied")
                var global_discount_amount = Math.abs(global_discount.price_unit);
                var total = order.amount_total + global_discount_amount;
                var discount_ratio = global_discount_amount / parseFloat(total);
                var total_with_tax_amount = selectedOrder.get_total_with_tax();
                var discount_amount = discount_ratio * total_with_tax_amount;
                var product = global_discount.get_product();
                selectedOrder.add_product(product, {
                    price:  Math.abs(discount_amount),
                });
//            	    var orderlines = selectedOrder.get_orderlines();
//            	    console.log('orderlines');
//            	    for(var i=0; i < orderlines.length ; i++){
//            	        orderlines[i].price = orderlines[i].price *(1- discount_ratio);
//            	    }
            }

            	//return reorder_products;
            	Object.keys(reorder_products).forEach(function(line_id) {

            		//#########################################################################################


            		var orders_lines = self.pos.db.all_orders_line_list;
            		var orderline = [];
                       for(var n=0; n < orders_lines.length; n++){
                           if (orders_lines[n]['id'] == line_id){
                            var product = self.pos.db.get_product_by_id(orders_lines[n].product_id[0]);
                            selectedOrder.add_product(product, {
                                quantity: parseFloat(reorder_products[line_id]),
                                price: orders_lines[n].price_unit,
                                discount: orders_lines[n].discount
                            });
                            selectedOrder.selected_orderline.original_line_id = orders_lines[n].id;
                           }
                       }

                	});
            	selectedOrder.set_client(client);
            	self.pos.set_order(selectedOrder);
            	self.gui.show_screen('products');

               });
        },
    });
    gui.define_popup({
        name: 'pos_re_order_popup_widget',
        widget: PosReOrderPopupWidget
    });

    // End PosReOrderPopupWidget Popup start


//Barcode Pop up start

    var PosBarcodePopupWidget = popups.extend({
        template: 'PosBarcodePopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },

        show: function(options) {
        	options = options || {};
            var self = this;
            this._super(options);

        },

        events: {
            'click .button.cancel': 'click_cancel',
        },



        renderElement: function() {
            var self = this;
            this._super();
            var self = this;
            var selectedOrder = this.pos.get_order();
            var orderlines = self.options.orderlines;
            var order = self.options.order;
            var return_products = {};
		    var exact_return_qty = {};
            var exact_entered_qty = {};
            var orders = self.pos.db.all_orders_list;

            this.$('#apply_barcode_return_order').click(function() {
                self.on_click_barcode_return();
            });

        },

        on_click_barcode_return: function(){
            var self = this;
//            var entered_barcode = $("#entered_item_barcode").val();

            rpc.query({
                model: 'pos.order',
                method: 'return_order_by_barcode',
                args: [ $("#entered_item_barcode").val(),self.pos.config.id],

            }).then(function(order) {
                if(order){
                    if( !self.pos.db.get_orders_by_id[order.id]){
                        var order_date = new Date(order.date_order);
                        var order_date_local = moment(order_date).add(2, 'hours');
                        order.date_order = moment(order_date_local).format('YYYY-MM-DD HH:mm:ss');
                        self.pos.db.all_orders_list.unshift(order);
                        self.pos.db.get_orders_by_id[order.id] = order;
                    }
                    for(var ln=0; ln < order.ret_lines.length; ln++){
                        if(!self.pos.db.get_lines_by_id[order.ret_lines[ln].id]){
                            self.pos.db.all_orders_line_list.unshift(order.ret_lines[ln]);
                            self.pos.db.get_lines_by_id[order.ret_lines[ln].id] = order.ret_lines[ln];
                        }
                    }
                    self.gui.show_popup('pos_return_order_popup_widget', {'orderlines': order.ret_lines, 'order': order });
                }
                else{
                    self.pos.gui.show_popup('error', {
                        'title': _t('Invalid Barcode'),
                        'body': _t("The Barcode You are Entering is Invalid Or Expire"),
                    });
                }
            });


        },
    });

 //Barcode Pop up end


    // Popup start

    var PosReturnOrderPopupWidget = popups.extend({
        template: 'PosReturnOrderPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        //
        show: function(options) {
        	options = options || {};
            var self = this;
            this._super(options);
            this.orderlines = options.orderlines || [];

        },
        //
        renderElement: function() {
            var self = this;
            this._super();
            var selectedOrder = this.pos.get_order();
            var orderlines = self.options.orderlines;
            var order = self.options.order;

            // When you click on apply button, Customer is selected automatically in that order
            var partner_id = false
            var client = false
            if (order && order.partner_id != null)
                partner_id = order.partner_id[0];
                client = this.pos.db.get_partner_by_id(partner_id);

			var return_products = {};
			var exact_return_qty = {};
            		var exact_entered_qty = {};



            this.$('#apply_return_order').click(function() {
                var entered_code = $("#entered_item_qty").val();
                var list_of_qty = $('.entered_item_qty');


				$.each(list_of_qty, function(index, value) {
                    var entered_item_qty = $(value).find('input');
               	    var qty_id = parseFloat(entered_item_qty.attr('qty-id'));
               	    var return_qty = parseFloat(entered_item_qty.attr('nqty'));
		            var line_id = parseFloat(entered_item_qty.attr('line-id'));
		            var entered_qty = parseFloat(entered_item_qty.val());

		            exact_return_qty = qty_id;
                    exact_entered_qty = entered_qty || 0;

		            if(!exact_entered_qty){
		            	return;
                    }
                    else if ((return_qty + exact_entered_qty) > exact_return_qty){
                        alert('Cannot Return More quantity than purchased');
                        throw new Error('Cannot Return More quantity than purchased');
                    }
                    else if (exact_return_qty >= exact_entered_qty){
		              return_products[line_id] = entered_qty;
                    }
                    else{
                        alert('Cannot Return More quantity than purchased');
                        throw new Error('Cannot Return More quantity than purchased');
                    }

//				 	var entered_item_qty = $(value).find('input');
//               	    var qty_id = parseFloat(entered_item_qty.attr('qty-id'));
//		            var line_id = parseFloat(entered_item_qty.attr('line-id'));
//		            var entered_qty = parseFloat(entered_item_qty.val());
//
//		            exact_return_qty = qty_id;
//                    exact_entered_qty = entered_qty || 0;
//
//		            if(!exact_entered_qty){
//		            	return;
//                    }
//                    else if (exact_return_qty >= exact_entered_qty){
//		              return_products[line_id] = entered_qty;
//                    }
//                    else{
//                    alert("Cannot Return More quantity than purchased")
//                    }

            	});
            	//return return_products;


            	Object.keys(return_products).forEach(function(line_id) {

            		//##################### new code for sync with previous order #############################
            		var orders_lines = self.pos.db.all_orders_line_list;
            		var orderline = [];
                       for(var n=0; n < orders_lines.length; n++){
                           if (orders_lines[n]['id'] == line_id){

                           if(orders_lines[n].pack_lot_ids != [] || orders_lines[n].pack_lot_ids !=null ){
                           var lot_name;
                           var lot_id = orders_lines[n].pack_lot_ids[0]
                            var lot =  self.pos.db.get_lot_lines_by_id[lot_id]
                            if(lot){
                            if(lot['lot_name']){
                            lot_name=lot['lot_name']
                            }
                            }

                             var product = self.pos.db.get_product_by_id(orders_lines[n].product_id[0]);
                            selectedOrder.add_product(product, {
                                quantity: - parseFloat(return_products[line_id]),
                                price: orders_lines[n].price_unit,
                                discount: orders_lines[n].discount,
                                lot :lot_name,
                            });
                            selectedOrder.selected_orderline.original_line_id = orders_lines[n].id;
                           }

                           else{
                            var product = self.pos.db.get_product_by_id(orders_lines[n].product_id[0]);
                            selectedOrder.add_product(product, {
                                quantity: - parseFloat(return_products[line_id]),
                                price: orders_lines[n].price_unit,
                                discount: orders_lines[n].discount,
                            });
                            selectedOrder.selected_orderline.original_line_id = orders_lines[n].id;
                           }

                           }
                       }

            		//#########################################################################################

                Object.keys(return_products).forEach(function(line_id) {

            		//##################### new code for sync with previous order #############################
            		var orders_lines = self.pos.db.all_orders_line_list;
            		var orderline = [];
                       for(var n=0; n < orders_lines.length; n++){
                           if (orders_lines[n]['id'] == line_id){
                                    selectedOrder.selected_orderline.original_line_id = orders_lines[n].id;
                                    var return_qty = orders_lines[n].return_qty || 0;
                                    orders_lines[n].return_qty = return_qty + parseFloat(return_products[line_id]);
                           }
                       }

            		//#########################################################################################

            	});


            });
            var order = self.options.order;
            var global_discount = null;
            var lines = order.lines;
            for(var i = 0;i < lines.length; i++){
                var line_id  = lines[i];
                var line = self.pos.db.get_lines_by_id[line_id] ;
                if(line.price_unit < 0){
                    global_discount = line;
                }
            }
            console.log('global_discount');
            console.log(global_discount);
            if(global_discount){
//            	    console.log("global discount applied")
                var global_discount_amount = Math.abs(global_discount.price_unit);
                var total = order.amount_total + global_discount_amount;
                var discount_ratio = global_discount_amount / parseFloat(total);
                var total_with_tax_amount = selectedOrder.get_total_with_tax();
                var discount_amount = discount_ratio * total_with_tax_amount;
                var product_id = global_discount.product_id[0];
                var product = self.pos.db.get_product_by_id(product_id);
                console.log('product');
                console.log(product);
                selectedOrder.add_product(product, {
                    price:  Math.abs(discount_amount),
                });
//            	    var orderlines = selectedOrder.get_orderlines();
//            	    console.log('orderlines');
//            	    for(var i=0; i < orderlines.length ; i++){
//            	        orderlines[i].price = orderlines[i].price *(1- discount_ratio);
//            	    }
            }
            	selectedOrder.set_client(client);
            	self.pos.set_order(selectedOrder);
            	selectedOrder.name ='Return '+ selectedOrder.name;
                self.gui.show_screen('products');
//            	self.gui.show_screen('payment');
//                $('div.payment-screen.screen div.screen-content div.top-content span.button.next.highlight').trigger('click');


               });

        },

    });
    gui.define_popup({
        name: 'pos_return_order_popup_widget',
        widget: PosReturnOrderPopupWidget
    });

    gui.define_popup({
        name: 'pos_barcode_popup_widget',
        widget: PosBarcodePopupWidget
    });

    // End Popup start


	// Start SeeAllOrdersButtonWidget

    var SeeAllOrdersButtonWidget = screens.ActionButtonWidget.extend({
        template: 'SeeAllOrdersButtonWidget',

        button_click: function() {
            var self = this;
            if (self.pos.config.allow_return_password == true) {
                self.gui.show_popup('passwordinput', {
                    'title': _t('Password ?'),
                     confirm: function (pw) {
                        if (pw !== self.pos.config.return_order_password) {
                            self.gui.show_popup('error', {
                                'title': _t('Error'),
                                'body': _t('Incorrect password. Please try again'),
                            });
                        } else {
                            this.gui.show_screen('see_all_orders_screen_widget', {});
                        }
                        },
                    });
                } else {
                        this.gui.show_screen('see_all_orders_screen_widget', {});
                    }
//            this.gui.show_screen('see_all_orders_screen_widget', {});
        },

    });

    screens.define_action_button({
        'name': 'See All Orders Button Widget',
        'widget': SeeAllOrdersButtonWidget,
        'condition': function() {
            return true;
        },
    });
    // End SeeAllOrdersButtonWidget

var OrderSelectorWidget = chrome.OrderSelectorWidget.include({

neworder_click_handler: function(event, $el) {

if($(".select-order").length>=4){
$(".neworder-button").css("display","none");
}
 else{
 $(".neworder-button").css("display","block");

 this.pos.add_new_order();
 }
    },


});



var Chrome = chrome.Chrome.include({
    init: function() {
        var self = this;
 this.widgets[5].args.action = function(){
                    var self = this;
                    if (!this.confirmed) {
                    if($(".select-order").length>1){
                    alert('please close the opened orders first')
//                    this.gui.show_popup('error',_t('please close the opened orders first'));
            return;
                    }
                        this.$el.addClass('confirm');
                        this.$el.text(_t('Confirm'));
                        this.confirmed = setTimeout(function(){
                            self.$el.removeClass('confirm');
                            self.$el.text(_t('Close'));
                            self.confirmed = false;
                        },2000);
                    } else {
                        clearTimeout(this.confirmed);
                        //
                        this.gui.close();
                    }
                },
        this._super();

        },


});



// Start ClientListScreenWidget
		gui.Gui.prototype.screen_classes.filter(function(el) { return el.name == 'clientlist'})[0].widget.include({
            show: function(){
		        this._super();

		        var self = this;
		        this.$('.view-orders').click(function(){
            		self.gui.show_screen('see_all_orders_screen_widget', {});
            	});


            $('.selected-client-orders').on("click", function() {
                self.gui.show_screen('see_all_orders_screen_widget', {
                    'selected_partner_id': this.id
                });
            });

        },

    });
screens.ClientListScreenWidget.include({

    save_client_details: function(partner){

         var self = this;
        var fields = {};
        this.$('.client-details-contents .detail').each(function(idx,el){
            fields[el.name] = el.value || false;
        });

        if (!fields.name) {
            this.gui.show_popup('error',_t('A Customer Name Is Required'));
            return;
        }
//        if (!fields.email) {
//            this.gui.show_popup('error',_t('A Customer Email Is Required'));
//            return;
//        }
//         if (!fields.phone) {
//            this.gui.show_popup('error',_t('A Customer Phone Is Required'));
//            return;
//        }
        this._super(partner);

        },


    });



	// Start pos_invoice_auto_check
	screens.PaymentScreenWidget.include({
		// Include auto_check_invoice boolean condition in watch_order_changes method
		order_changes: function() {
		    var self = this;
		    var order = this.pos.get_order();
		    var total = order.get_total_with_tax();


         var due   = order.get_due();
        var change   = order.get_change();

		    if(total<0){
		    $(".paymentmethod:first-child").siblings().css("display","none");

		    }
		    else{
		    $(".paymentmethod:first-child").siblings().css("display","block");
		    }
		           this._super();

		},
		watch_order_changes: function() {
		    var self = this;
		    var order = this.pos.get_order();

		    if(this.pos.config.auto_check_invoice) // Condition True/False
				{
					var pos_order=this.pos.get_order();
					pos_order.set_to_invoice(true);
					this.$('.js_invoice').hide();
				}


		    if (!order) {
		        return;
		    }
		    if(this.old_order){
		        this.old_order.unbind(null,null,this);
		    }
		    order.bind('all',function(){
		        self.order_changes();
		    });
		    this.old_order = order;
		},


    });
    // End pos_invoice_auto_check

    screens.ReceiptScreenWidget.include({
        renderElement: function () {
            var self = this;
            this._super();
            this.$('.back_order').click(function () {
                var order = self.pos.get_order();
                if (order) {
                    self.pos.gui.show_screen('products');
                }
            });
        },
        show: function () {
            this._super();
            try {
                JsBarcode("#barcode", this.pos.get('selectedOrder').barcode, {
                    format: "EAN13",
                    displayValue: true,
                    fontSize: 25
                });
            } catch (error) {
            console.log(error);
            }

//            if(this.pos.config.iface_print_auto){
//                setTimeout(function(){
//                this.$('.receipt-screen .print').click();
//            }, 1000);
//            }
        },

        handle_auto_print: function() {
            if (this.should_auto_print()) {

                setTimeout(function(){
                    this.print();
                }, 2000);
                if (this.should_close_immediately()){
//                setTimeout(function(){
                    this.click_next();
//                }, 1000);

                }
            } else {
                this.lock_screen(false);
            }
        },

    });



   screens.ProductScreenWidget.include({

        _handleBufferedKeys: function () {
            // If more than 2 keys are recorded in the buffer, chances are high that the input comes
            // from a barcode scanner. In this case, we don't do anything.
            if (this.buffered_key_events.length > 2) {
                this.buffered_key_events = [];
                return;
            }

            for (var i = 0; i < this.buffered_key_events.length; ++i) {
                var ev = this.buffered_key_events[i];
                if ((ev.key >= "0" && ev.key <= "9") || ev.key === ".") {
                   this.numpad.state.appendNewChar(ev.key);
                }
                else {
                    switch (ev.key){
                        case "Backspace":
                            this.numpad.state.deleteLastChar();
                            break;
                        case "Delete":
                            this.numpad.state.resetValue();
                            break;
                        case ",":
                            this.numpad.state.appendNewChar(".");
                            break;
//                        case "+":
//                            this.numpad.state.positiveSign();
//                            break;
//                        case "-":
//                            this.numpad.state.negativeSign();
//                            break;
                    }
                }
            }
            this.buffered_key_events = [];
        },
    })





})
