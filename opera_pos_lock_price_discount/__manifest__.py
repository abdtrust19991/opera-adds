# -*- coding: utf-8 -*-

{
    'name': "POS LOCK PRICE DISCOUNT",
    'summary': """
        Lock change price or discount in Point Of Sale""",
    'description': """
        This module add features to lock change price or discount in Point Of Sale using password
    """,
    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",
    'category': 'Point Of Sale',
    'license': "LGPL-3",
    'version': '14.0.1.0',
    'images': ['images/cover.jpg'],
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'wizard/pos_session_close_wizard.xml',
        'views/pos_config_view.xml',
        'views/pos_session.xml',
    ],
    'qweb': [
        'static/src/xml/PasswordInputPopupWidget.xml',
        'static/src/xml/NumpadWidget.xml',
    ],
    'price': '0',
    'currency': 'EUR',
}
