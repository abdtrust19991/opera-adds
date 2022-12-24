# -*- coding: utf-8 -*-
{
    'name': 'Payment Restrictions',
    'version': '11.0.2',
    'summary': 'Limit Access To Payment For Each User',
    'author': 'Ahmed Amen',
    'website': 'https://itss-c.com',
    'category': 'Payment Management',
    'depends': ['base','account'],
    'data': [
        'views/res_users.xml',
        'views/payment.xml',
        'security/payment_access.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
