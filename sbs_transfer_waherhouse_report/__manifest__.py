# -*- coding: utf-8 -*-
{
    'name': "sbs_transfer_waherhouse_report",

    'summary': """
        Waherhouse Report""",

    'description': """
         Waherhouse Report
    """,

    'author': "Mohammed AbdelBaset",
    'version': '13.0.1',

    'depends': ['base','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'reports/warehouse_report.xml',
    ],

}