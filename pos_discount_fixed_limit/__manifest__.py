# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.
{
    'name': 'POS Global Discounts - Fixed/Percentage(Cash Discount)',
    'version': '14.0.0.1',
    'category': 'Point of Sale',
    'sequence': 1,
    'summary': 'Fixed/Percentage Global Discounts(Cash Discount) in the Point of Sale ',
    'description': """
This module allows the cashier to quickly give a fixed/percentage
sale discount(cash discount) to a customer.
""",
    'website': 'http://www.technaureus.com',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'price': 55,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'depends': ['pos_discount', 'user_discount_limit'],
    'data': [
        'data/point_of_sale_data.xml',
        'views/pos_discount_views.xml',
        'views/pos_discount_templates.xml'
    ],
    'qweb': [
        'static/src/xml/discount_templates.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
