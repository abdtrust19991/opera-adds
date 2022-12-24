# -*- coding: utf-8 -*-
{
    'name': "accerps_internal_transfers",

    'summary': """
        Inter-transfers location""",

    'description': """
        Inter-transfers location
    """,

    'author': "SBS",
    'website': "http://www.accerps.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_limitation', 'hr_expense'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/accerps_internal_transfers_security.xml',
        'views/views.xml',
        # 'views/res_config_settings_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
