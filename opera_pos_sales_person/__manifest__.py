# -*- coding: utf-8 -*-
{
    'name': "Pos Sales Person",

    'summary': """
        Pos Sales Person """,


    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",

    'category': 'point of sale',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'point_of_sale',
        'hr'
    ],

    # always loaded
    'data': [
        'views/templates.xml',
        'views/hr_employee.xml',
        'views/pos_order.xml',
        'views/pos_config.xml',
    ],
    'qweb': [
        'static/src/xml/sale_person.xml',
        'static/src/xml/OrderList.xml',
        'static/src/xml/OrderRow.xml',
    ],



}