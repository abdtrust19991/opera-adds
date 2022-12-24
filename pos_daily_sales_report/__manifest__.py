# -*- coding: utf-8 -*-
#############################################################################


{
    'name': 'POS Daily Sales Report',
    'version': '14.0.1.0.0',
    'summary': """Print POS Daily Sales Report """,
    'description': """Print POS Daily Sales Report""",
    'author': "Ahmed Amen",
    'category': 'Sales',
    'depends': ['base', 'point_of_sale'],
    'data': [
         'security/ir.model.access.csv',
         'views/template.xml',
         'views/pos_method.xml',
         'views/pos_user_print.xml',
         'wizard/report_wizard.xml',
             ],
}

