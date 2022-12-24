# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name' : 'Manufacturing Reset to Draft',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Manufacturing',
    'maintainer': 'Craftsync Technologies',
   
    'summary': """Manufacturing Reset to Draft app is helpful plugin to reset cancelled manufacturing order.""",

    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
     'depends' : ['mrp'],
    'data': [
	    'views/view_manufacturing_order.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 10.00,
    'currency': 'EUR',

}
