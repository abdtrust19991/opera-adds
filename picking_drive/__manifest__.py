# coding: utf-8
##############################################################################
#this is for me 'A7med Amin
##############################################################################

{
    'name': 'Picking Driver',
    'version': '12',
    'author': 'Ahmed Amen',
    'license': 'AGPL-3',
    'category': 'Inventory',
    'summary': 'Add driver person for picking',
    'depends': ['base',
                'stock',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/picking.xml',
    ],
    'installable': True,
    'demo': [],
    'test': []
}
