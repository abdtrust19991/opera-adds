# -*- coding: utf-8 -*-
{
    'name': "Accounting Petty Cash Management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Eng.Ramadan Khalil",
    'website': "http://www.itss-c.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'account',
    'version': '0.6',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','hr','hr_expense'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/petty_cash_data.xml',
        'views/payment_view.xml',
        'views/petty_cash_type_view.xml',
        'views/petty_view.xml',
        'wizard/petty_pay_wizard_view.xml',
        'views/hr_expense_view.xml',
        'views/account_invoice_view.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
