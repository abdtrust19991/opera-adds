# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	"name" : "All pos orders list in Odoo ",
	"version" : "14.0.0.0",
	"category" : "Point of Sale",
	"depends" : ['base','sale','point_of_sale'],
	"author": "BrowseInfo",
	'summary': 'Apps manage point of sale orders from the POS screen pos all order list pos order list pos list point of sales list Pos All Orders List on POS screen pos orderlist pos all orderlist list pos list orders pos all orders display pos orders list pos all orders',
	'price': 18,
	'currency': "EUR",
	"description": """
	
point of sale orderlist pos orderlist odoo pos orders manage pos orders in odoo edit pos orders from pos screen 
	Purpose :- 
pos all list orders all orders pos all list orders pos pos all orders
all point of sales orders all orders list All pos orders list All pos order lists
pos All orders list pos all orders point of sales all orders point of sales order list 
pos orderlist pos all orderlist list of all order pos odoo manage all order list odoo manage pos all order list
see the list of all the orders within a running POS Screen. 

point of sale all list orders all orders point of sale all list orders point of sales point of sale all orders
all pos orders all orders list All point of sale orders list All point of sale order lists
point of sale All orders list point of sale all orders point of sales all orders point of sales order list 
point of sale orderlist point of sale all orderlist list of all order point of sale odoo manage all order list odoo manage point of sale all order list
see the list of all the orders within a running point of sale Screen. 

point of sales all list orders all orders point of sales all list orders point of sales point of sales all orders
all in one pos orders all orders list All point of sales orders list All point of sales order lists
point of sales All orders list point of sales all orders point of sales all orders point of sales order list 
point of sales orderlist point of sales all orderlist list of all order point of sales odoo manage all order list odoo manage point of sale all order list
see the list of all the orders within a running point of sales Screen. 
pos order list on pos point of sale order list on point of sales order list on point of sales

 Currently in Odoo point of sales doesn't allow to reprint order once validate order, this odoo apps module allows to reprint all order again if you required sometimes its important, its obvious we need to reprint all orders.

It shows the Pos All Orders List on POS screen View all POS order on screen. 
This apps helps to manage point of sale orders from the POS screen
List all POS order on POS screen Show order on POS view all orders on POS Display order on POS View order on POS
	""",
	"website" : "https://www.browseinfo.in",
	"data": [
		'views/assets.xml',
		'views/custom_pos_view.xml',
	],
	'qweb': [
		'static/src/xml/pos_orders_list.xml',
	],
	"auto_install": False,
	"installable": True,
	"live_test_url":'https://youtu.be/IJvQjjWNqsM',
	"images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
