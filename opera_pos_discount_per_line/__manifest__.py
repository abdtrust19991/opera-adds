
{
    'name': 'Pos Discount Per Line',
    'summary': 'Pos Discount Per Line',
    'author': "ITSS , Mahmoud Elfeky",
    'company': 'ITSS',
    'website': "http://www.itss-c.com",
    'version': '14.0.0.1.0',
    'category': 'Point Of Sale',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'point_of_sale',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'report/',
        # 'wizard/',
        'views/pos_discount_templates.xml',
        'views/pos_discount_views.xml',
        # 'data/',
    ],
    'qweb': [
        'static/src/xml/DiscountButton.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

