# -*- coding: utf-8 -*-
{
    'name': "Purchase Plan",

    'summary': """
        this model allow to make a plan for purchases """,


    'author': "Ahmed Amen",
    'website': "http://www.itss-c.com",

    'category': 'Purchase',
    'version': '12.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_plan.xml',
        'views/purchase.xml',
        'views/assets.xml',

    ],



}
