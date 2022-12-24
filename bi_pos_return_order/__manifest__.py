# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	"name" : "POS Order Return With Barcode Scanner in Odoo",
	"version" : "14.0.0.0",
	"category" : "Point of Sale",
	'summary': 'return product from POS screen return order from POS screen pos return order pos rma order Product Return In POS point of sales return orders POS Orders Return pos refund order pos order return pos item return sale from pos Return with Barcode Scanner ',
	"depends" : ['base','point_of_sale','pos_orders_list'],
	"author": "BrowseInfo",
	'price': 19,
	'currency': "EUR",
	"description": """
This Module Helps a return orders from the POS.
Also it helps to return the product from POS. Also able to return whole order from POS screen.
Return product from POS screen Return product from POS Screen POS return product pos
POS product return POS order return Order Return from POS Product Return from POS
POS Revise Order POS Product Return Revise POS Order Cancel POS Order Cancel Order pos


Also it helps to return the product from Point of Sale. Also able to return whole order from Point of Sale screen.
Return product from Point of Sale screen Return product from Point of Sale Screen Point of Sale return product point of sales
Point of Sale product return Point of Sale order return Order Return from Point of Sale Product Return from Point of Sales
Point of Sale Revise Order Point of Sale Product Return Revise Point of Sale Order Cancel Point of Sale Order Cancel Order Point of Sale

Also it helps to return the product from Point of Sales. Also able to return whole order from Point of Sales screen.
Return product from Point of Sales screen Return product from Point of Sales Screen Point of Sales return product pos
Point of Sales product return Point of Sals order return Order Return from Point of Sales Product Return from Point of Sales
Point of Sales Revise Order Point of Sales Product Return Revise Point of Sales Order Cancel Point of Sales Order Cancel Order Point of Sales
	
pos return with barcode scanner product return from barcode scanner on POS
barcode scanner pos return pos barcode return pos barocode order return order return from barcode 
pos scan order return pos return order scan product barcode return pos product barcode return

Point of Sales return with barcode scanner product return from barcode scanner on POS
barcode scanner Point of Sales return Point of Sales barcode return Point of Sales barocode order return order return from barcode 
Point of Sales scan order return Point of Sales return order scan product barcode return Point of Sales product barcode return

Point of Sale return with barcode scanner product return from barcode scanner on POS
barcode scanner Point of Sale return Point of Sale barcode return Point of Sale barocode order return order return from barcode 
Point of Sale scan order return Point of Sale return order scan product barcode return Point of Sale product barcode return

POS Revise POS Order Cancel POS Order Cancel Order.

pos Return product from barcode scanner. 
point of sale Return product from barcode scanner. point of sales Return product from barcode scanner.
POS return product with barcode scanner POS product return with barcode scanner.
POS order return with barcode scanner Order Return on POS with barcode scanner Product Return from POS using barcode scanner,
POS Revise Order using barcode scanner POS Product Return using barcode scanner.

point of sales return product with barcode scanner point of sales product return with barcode scanner.
point of sales order return with barcode scanner Order Return on point of sales with barcode scanner Product Return from point of sales using barcode scanner,
point of sales Revise Order using barcode scanner point of sales Product Return using barcode scanner.


point of sale return product with barcode scanner point of sale product return with barcode scanner.
point of sale order return with barcode scanner Order Return on point of sale with barcode scanner Product Return from point of sale using barcode scanner,
point of sale Revise Order using barcode scanner point of sale Product Return using barcode scanner.
	""",
	"website" : "https://www.browseinfo.in",
	"data": [
		'views/custom_pos_view.xml',
	],
	'qweb': [
		'static/src/xml/return_order.xml',
		# 'static/src/xml/pos_return_order.xml',
	], 
	"auto_install": False,
	"installable": True,
	"live_test_url": "https://youtu.be/wcSGlSZPZug",
	"images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
