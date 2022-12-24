odoo.define('opera_pos_sales_person.SalePersonButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    var models = require('point_of_sale.models');
    var Persons;

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        initialize: function (session, attributes) {
            this.models.push({
                model:  'hr.employee',
                fields: ['id','name','pos_code'],
                domain: function(self){ return [['id','in',self.config.sale_persons_ids]]; },
                loaded: function(self, sale_persons){
                    self.db.sale_persons = sale_persons;
                    Persons= sale_persons;
//                    console.log(sale_persons);
                }
            })
            return _super_posmodel.initialize.call(this, session, attributes);
        },

    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

            export_as_JSON: function(){
                var json = _super_order.export_as_JSON.apply(this,arguments);
                if (this.sale_person_code) {
                    json.sale_person_code = this.sale_person_code;
                }
                if (this.sale_person_name) {
                    json.sale_person_name = this.sale_person_name;
                }
                if (this.sale_person_id) {
                    json.sale_person_id = this.sale_person_id;
                }
                return json;
            },

            init_from_JSON: function(json){
                _super_order.init_from_JSON.apply(this,arguments);
                this.sale_person_id = json.sale_person_id;
                this.sale_person_code = json.sale_person_code;
                this.sale_person_name = json.sale_person_name;
            },
    })

    class SalePersonButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }

        async onClick() {

            const currentOrder = this.env.pos.get_order();
            if (currentOrder.return_order_id ){
                this.showPopup('ErrorPopup', {
                    title: _('Sales Person can not be changed for return orders!'),
                });
                return ;
            }
            let default_sale_person_id = this.env.pos.config.default_employee_id[0];
            let sale_person_id = currentOrder.sale_person_id;
            sale_person_id = sale_person_id ? sale_person_id : default_sale_person_id;
            const selectionList = [ ];
//            console.log(Persons);
            for (let person of Persons) {
                selectionList.push({
                    id: person.id,
                    label: person.name,
                    isSelected: sale_person_id
                        ? person.id === sale_person_id
                        : false,
                    item: person,
                });
            }
            const { confirmed, payload: selectedSalePerson } = await this.showPopup(
                'SelectionPopup',
                {
                    title: this.env._t('Select the Sale Person'),
                    list: selectionList,
                }
            );
            if (confirmed) {
//            console.log(selectedSalePerson.pos_code)
                currentOrder.sale_person_id = selectedSalePerson.id;
                currentOrder.sale_person_code = selectedSalePerson.pos_code;
                currentOrder.sale_person_name = selectedSalePerson.name;
                currentOrder.trigger('change');
                $('.sale_person').text(selectedSalePerson.name);
            }
        }
    }
    SalePersonButton.template = 'SalePersonButton';

    ProductScreen.addControlButton({
        component: SalePersonButton,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(SalePersonButton);

    return SalePersonButton;
});
