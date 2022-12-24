# -*- coding: utf-8 -*-
{
    "name": "Stocks Access Rules",
    "version": "13.0.1.0.1",
    "category": "Warehouse",
    "author": "faOtools",
    "website": "https://faotools.com/apps/13.0/stocks-access-rules-439",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "stock"
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/stock_view.xml",
        "views/res_users_view.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to restrict users' access to stocks, locations and warehouse operations",
    "description": """

For the full details look at static/description/index.html

- The tool is often used along with the &lt;a href=&quot;https://apps.odoo.com/apps/modules/13.0/product_stock_balance&quot;&gt;module 'Stock by Locations'&lt;/a&gt;

* Features * 

- Access for inventory operation based on stock location settings

- Simple configuration

- Full coverage and super rights

- Compatible with standard features
 
* Extra Notes *



#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "28.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=71&ticket_version=13.0&url_type_id=3",
}