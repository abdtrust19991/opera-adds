# -*- coding: utf-8 -*-
{
    'name': 'Account Payment in POS',
    'version': '11.0.2',
    'summary': 'Add form of Account Payment in POS',
    'author': 'Ahmed Amen',
    'website': 'https://itss-c.com',
    'category': 'Payment Management',
    'depends': ['account','point_of_sale'],
    'data': [
        'views/payment.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
