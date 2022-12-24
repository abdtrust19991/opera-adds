odoo.define('opera_pos_customizations.NumpadWidget', function (require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');

    var _t = core._t;

    const NumpadWidgetInherit = NumpadWidget => class extends NumpadWidget {

        sendInput(key) {
            var decimal_separator = super.decimalSeparator;
            if(this.props.activeMode === 'quantity' && key === decimal_separator ){
                var selected_line = this.env.pos.get_order().get_selected_orderline() ;
                if(selected_line){
                    var uom = selected_line.get_unit();
                    if(uom.disable_fraction){
                        alert(_t(
                            "Fraction is disabled for this Unit"
                        ));
                        return;
                    }
                }

            }
            super.sendInput(key) ;
        }

    }

    Registries.Component.extend(NumpadWidget , NumpadWidgetInherit);

    return NumpadWidget;
    
})