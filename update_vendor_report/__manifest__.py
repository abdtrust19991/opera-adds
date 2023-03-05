# -*- coding: utf-8 -*-
{
    'name': "Update Vendor Report",

    'summary': """
       Update module vendor_report show list of stock move details """,


    'author': "Sary Babiker",
    'category': 'inventory',
    'version': '14.0.0.1',

    # This module update to original module vendor_report so depend on it
    'depends': ['vendor_report'],

    'data': [
        'wizard/up_report_wizard.xml',
    ],



}