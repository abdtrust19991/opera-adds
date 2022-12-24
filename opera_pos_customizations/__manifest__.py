# -*- coding: utf-8 -*-

{
    'name': "opera Kids POS Customizations",
    'summary': """
        opera Kids POS Customizations""",
    'description': """
        opera Kids POS Customizations
    """,
    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",
    'category': 'Point Of Sale',
    'license': "LGPL-3",
    'version': '14.0.1.0',
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml',
        # 'views/pos_config_view.xml',
        'views/res_partner.xml',
        'views/uom_uom.xml',
    ],
    'qweb': [
        'static/src/xml/OrderWidget.xml',
        'static/src/xml/OrderSummary.xml',
        'static/src/xml/PaymentMethodButton.xml',
    ],
}
