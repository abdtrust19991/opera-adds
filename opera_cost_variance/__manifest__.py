
{
    'name': 'Alma Cost Variance',
    'summary': 'Alma Cost Variance',
    'author': "ITSS , Mahmoud Elfeky",
    'company': 'ITSS',
    'website': "http://www.itss-c.com",
    'version': '14.0.0.1.0',
    'category': 'MRP',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'mail',
        'account',
        'mrp',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'report/',
        # 'wizard/',
        'views/account_account.xml',
        'views/cost_variance.xml',
        # 'data/',
    ],
    'demo': [
        # 'demo/',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

