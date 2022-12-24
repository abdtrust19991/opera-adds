# -*- coding: utf-8 -*-
{
    'name': "Product Barcode Print Out",

    'summary': """
        Product Barcode Print Out """,

    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",

    'category': 'Product',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_barcode_wizard.xml',
        'views/templates_first_label.xml',
        'views/product_product.xml',

    ],



}