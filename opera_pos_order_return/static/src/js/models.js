odoo.define('pos_order_return_and_reprint.models', function(require) {
"use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    const { Gui } = require('point_of_sale.Gui');
    var _t = core._t;


    var existing_models = models.PosModel.prototype.models;
    var payment_index = _.findIndex(existing_models, function (model) {
        return model.model === "pos.payment.method";
    });
    var payment_model = existing_models[payment_index];

    models.load_models([{
        model:  payment_model.model,
        fields: payment_model.fields,
        order:  payment_model.order,
        domain: function(self) {return []},
        context: payment_model.context,
        loaded: function(self, payment_methods) {
            _.each(payment_methods, function(payment_method) {
                self.payment_methods_by_id[payment_method.id] = payment_method;
            })
        }
    }]);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

        generate_unique_id: function() {
            // Generates a public identification number for the order.
            // The generated number must be unique and sequential. They are made 12 digit long
            // to fit into EAN-13 barcodes, should it be needed

            function zero_pad(num,size){
                var s = ""+num;
                while (s.length < size) {
                    s = "0" + s;
                }
                return s;
            }
            var date = new Date();
            var hours = date.getHours();
            var minutes = date.getMinutes();
            var seconds = date.getSeconds();
            return zero_pad(this.pos.pos_session.id,5) +'-'+
                   zero_pad(this.pos.pos_session.login_number,3) +'-'+
                   zero_pad(this.sequence_number,4) +'-'+zero_pad(hours,2)+
                   zero_pad(minutes,2) +zero_pad(seconds,2);
        },

        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            if (this.barcode) {
                json.barcode = this.barcode;
            }
            if (this.return_order_id) {
                json.return_order_id = this.return_order_id;
            }
//            if(this.bank_payment_journal_ids){
//                json.bank_payment_journal_ids = this.bank_payment_journal_ids;
//            }
//            if(this.cash_payment_journal_id){
//                json.cash_payment_journal_id = this.cash_payment_journal_id;
//            }
            if (!this.barcode && this.uid) { // init barcode and automatic create barcode for order
                var barcode = '9';
                var uid = this.uid;
                uid = uid.substring(1);
                var fbarcode = uid.split('-');
//                for (var i in fbarcode) {
//                    barcode += fbarcode[i];
//                }
                barcode += fbarcode[0];
                barcode += '0';
                barcode += fbarcode[3];

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
            if (json.return_order_id) {
                this.return_order_id = json.return_order_id;
            }
//            if(json.bank_payment_journal_ids){
//                this.bank_payment_journal_ids = json.bank_payment_journal_ids;
//                if(res){
//                    res.bank_payment_journal_ids = json.bank_payment_journal_ids;
//                }
//            }
//            if(json.cash_payment_journal_id){
//                this.cash_payment_journal_id = json.cash_payment_journal_id;
//                if(res){
//                    res.cash_payment_journal_id = json.cash_payment_journal_id;
//                }
//            }

            return res;
        },

        set_client: function(client){
            if (this.return_order_id){
               Gui.showPopup('ErrorPopup', {
                    title: _t('You Can not change client of returned orders'),
                    body: _t('You Can not change client of returned orders'),
                });
                return;
            }
            _super_order.set_client.apply(this, arguments);
        },



    })

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({

        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.order_line_id  = json.order_line_id;
            this.return_qty  = json.return_qty;
        },
        export_as_JSON: function() {
           var json = _super_orderline.export_as_JSON.apply(this,arguments);
            if (this.order_line_id){
                json.order_line_id = this.order_line_id;
            }
            json.return_qty = this.return_qty;
            return json;
        },

        get_total_return_qty: function(){
            return this.return_qty || 0;
        },
    })

})
