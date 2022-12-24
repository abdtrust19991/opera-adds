# -*- coding: utf-8 -*-
{
    'name': """ Stock Quantity Notifications """,
    'summary': """Automatic Notification For Reaching Min Quantity.""",
    'author': "Omnia Sameh, ITSS <https://www.itss-c.com>",
    "version": "12.0.1.0.0",
    'depends': ['stock'],
    'category': 'warehouse',
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/stock_minimum_quantity.xml',
    ],
    "license": 'AGPL-3',
    'installable': True,
}
