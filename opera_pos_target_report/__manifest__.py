# -*- coding: utf-8 -*-
{
    'name': "POS Target",

    'summary': """
        report show Target details """,


    'author': "Ahmed Amen",
    'category': 'point of sale',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/target_view.xml',
        'views/targit_temp.xml',
        'wizard/target_report_wizard.xml',
    ],



}