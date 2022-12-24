# -*- coding: utf-8 -*-
{
    'name': "Items Report",

    'summary': """
        report show Target details """,


    'author': "Ahmed Amen",
    'category': 'point of sale',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale','stock','sale','purchase','product_category'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_wizard.xml',
    ],



}