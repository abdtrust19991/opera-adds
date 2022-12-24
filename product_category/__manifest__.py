# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Create Product Based On Category',
    'version': '1.6',
    'category': 'Sale',
    'author': 'Ahmed Amen',
    'sequence': 6,
    'summary': 'Create Product Based On Category ',
    'description': """
    This module allows to Create Product Based On Category.   
    
    Function : 
   
    *   create number of product = No of models you entered. \n
    *   name of every product created is name of category + sequence.\n
    *   barcode generated  by fields you entered year, manufacture,season and sequence. \n

""",
    'depends': ['sale','stock','product','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/manufacture.xml',
        'views/year.xml',
        'views/season.xml',
        'views/activity.xml',
        'views/color.xml',
        'views/size.xml',
        'wizard/product_create_views.xml',
        'views/view.xml',


    ],
    'qweb': [
        # 'static/src/xml/btn_create.xml',
    ],
    'installable': True,
}
