odoo.define("pos_discount_fixed_limit.models", function (require) {
"use strict";

var models = require('point_of_sale.models');

models.load_fields('res.users',['fixed_limit','percentage_limit']);

})
