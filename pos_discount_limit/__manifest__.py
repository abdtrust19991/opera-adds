# -*- coding: utf-8 -*-

{
    'name': "POS Discount Limit",
    'summary': """
        This module restrict discount global in pos.""",
    'description': """
        This module restrict discount global in pos.""",
    'version': '13.0',
    'author': "Smart Business Solutions",
    'website': "http://www.accerps.com",
    'company': 'Smart Business Solutions',
    'maintainer': '',
    'category': 'Point of Sale',
    'depends': ['pos_discount'],
    'sequence': 99,
    'data': [
        'views/templates.xml',
        'views/pos_discount_limit_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}