# -*- coding: utf-8 -*-
{
    'name': "Electronic invoice KSA - POS | qrcode | ZATCA | vat | e-invoice | tax | Zakat",
    "version" : "14.0.0.1",
    "category" : "Accounting",
    'description': """
        Electronic invoice KSA - POS
    """,
    'author': "Era group",
    'email': "aqlan@era.net.sa ",
    'website': "https://era.net.sa",
    'category': 'accounting',
    'price': 0,  
    'currency': 'USD',
    'version': '0.1',
    'license': 'AGPL-3',
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base', 'account', 'point_of_sale',],
    'data': [
        'views/pos_config.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],

}
