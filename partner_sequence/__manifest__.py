
{
    'name': 'Partner Sequence',
    'summary': 'Partner Sequence',
    'author': "ITSS , Mahmoud Elfeky",
    'company': 'ITSS',
    'website': "http://www.itss-c.com",
    'version': '14.0.0.1.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'report/',
        # 'wizard/',
        'views/res_partner.xml',
        'data/sequence.xml',
    ],
    'demo': [
        # 'demo/',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

