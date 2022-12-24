# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Pos Discount Limitation",
    'summary': """
        Restrict users when applying Discount.
        """,
    'description': """
        Restrict users when applying Discount.
        """,
    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    # Categories can be used to filter modules in modules listing
    'category': 'Point of Sale',
    'version': '12.0.1.0.0',
    # any module necessary for this one to work correctly
    'depends': ['pos_discount'],
    'images': ['static/description/banner.png'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/point_of_sale_data.xml',
        'views/pos_discount_view.xml',
        'views/pos_discount_templates.xml',
    ],
}
