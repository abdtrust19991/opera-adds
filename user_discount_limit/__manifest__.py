# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today  Technaureus Info Solutions Pvt.Ltd.(<http://technaureus.com/>)

{
    'name': 'Discount Limit',
    'version': '13.0.1.1',
    'sequence': 1,
    'category': 'Point of Sale',
    'summary': 'Users discount limit',
    'description': """
This module allows user to set discounts for a customer.
    """,
    'author': "Technaureus Info Solutions Pvt. Ltd.",
    'website': "http://www.technaureus.com",
    'price': 10,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'depends': ['base'],
    'data': [
        'views/res_users_view.xml',
    ],
    'css': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,

}
