# -*- coding: utf-8 -*-
{
    'name': "pos orders return",

    'summary': """
        return pos orders in point of sale """,


    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",

    'category': 'point of sale',
    'version': '1.3',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale','pos_branches'],

    # always loaded
    'data': [
        'views/templates.xml',
        'views/pos_order.xml',
        'views/pos_config.xml',
    ],

    'qweb': [
        'static/src/xml/PosBarcodePopup.xml',
        'static/src/xml/PosReturnButton.xml',
        'static/src/xml/PosBarcodeReturnButton.xml',
        'static/src/xml/PosReturnOrderPopup.xml',
        'static/src/xml/ProductItem.xml',
        'static/src/xml/Orderline.xml',

    ],

}