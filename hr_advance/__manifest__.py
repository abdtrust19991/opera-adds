# coding: utf-8
##############################################################################
#this is for me 'A7med Amin
##############################################################################

{
    'name': 'HR Advance Salary',
    'version': '11.12',
    'author': 'Ahmed Amin',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'summary': 'Manage Employee Advance Salary Request',
    'depends': ['base',
                'account',
                'sale',
                'hr',
                'hr_payroll',
                ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/pay_wizard.xml',
        'wizard/close_wizard.xml',
        'wizard/close_advances.xml',
        'views/advance_salary.xml',
        'views/advance_type.xml',
        'views/employee.xml',
        'views/journal.xml',
    ],
    'installable': True,
    'application': True,
    'demo': [],
    'test': []
}
