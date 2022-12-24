odoo.define('opera_pos_lock_price_discount.NumberBuffer', function(require) {
    'use strict';

    const NumberBuffer = require('point_of_sale.NumberBuffer');

    NumberBuffer._onKeyboardInput =  function(event) {

        if( ['+','-','.','Backspace','Delete'].includes(event.key) ){
            return;
        }
        return this._bufferEvents(this._onInput(event => event.key))(event);
    }

});
