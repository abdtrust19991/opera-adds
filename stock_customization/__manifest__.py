
{
    'name': 'Stock Customization',
    'summary': 'Stock Customization',
    'author': "ITSS , Mahmoud Elfeky",
    'company': 'ITSS',
    'website': "http://www.itss-c.com",
    'version': '14.0.0.1.0',
    'category': 'Stock',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'stock',
        'stock_limitation',
        'point_of_sale',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'report/',
        # 'wizard/',
        'views/pos_order.xml',
        # 'data/',
    ],
    'demo': [
        # 'demo/',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

