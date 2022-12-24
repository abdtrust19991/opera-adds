# -*- coding: utf-8 -*-
{
    'name': "pos branches",

    'summary': """
        divide point of sale into branches """,


    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",

    'category': 'point of sale',
    'version': '1.3',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/pos_branch.xml',
        'views/pos_config.xml',
    ],



}