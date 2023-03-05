# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _
import pytz
import xlwt
import odoo.osv.osv
import re
import base64
from io import BytesIO
import datetime
from datetime import date, time
import pytz

from pytz import timezone

class VendortReportWizard(models.TransientModel):
    _inherit = 'vendor.report.wizard'


    type = fields.Selection([('per_product', 'Product'),
                             ('product_var', 'Product Variants'),
									('per_vendor', 'Vendor'),
									], string='view type', required=True,
									default='per_vendor')

    def get_report_data(self):
        data = []
        product_ids = self.env['product.template'].search([])
        if not self.vendor_id and self.type == 'product_var':
            total_qty_in = 0.0
            total_sale_qty = 0.0
            products = self.env['product.product'].search([('product_tmpl_id', 'in', product_ids.ids), ('id', '!=', self.id)])
            for vari in products:
                move_purchase = self.env['stock.move'].sudo().search([
                            ('product_id', '=', vari.id),
                            ('state','=','done'),
                            ('purchase_line_id', '!=', False), ('picking_code', '=', 'incoming')
                ])

                move_sales_in = self.env['stock.move'].sudo().search([
                    ('product_id', '=', vari.id),
                    ('state', '=', 'done'),
                    ('sale_line_id', '!=', False), ('picking_code', '=', 'outgoing')
                ])
            
                
                for move in move_purchase:
                    total_qty_in = move.product_uom_qty
                    if total_qty_in > 0.0:
                        sales_per = move_sales_in.product_uom_qty / total_qty_in * 100
                    else:
                        sales_per = 0.0
                    data.append({
                        'vendor':move.purchase_line_id.partner_id.name,
                        'product':move.name,
                        'avalible_qty':move.product_id.qty_available,
                        'qty': total_qty_in,
                        'sale_qty':move_sales_in.product_uom_qty,
                        'sales_per': sales_per,
                    })
        
        #  List product variant by select vendot
        elif self.vendor_id and self.type == 'product_var':
            total_qty_in = 0.0
            total_sale_qty = 0.0
            products = self.env['product.product'].search([('product_tmpl_id', 'in', product_ids.ids), ('id', '!=', self.id)])
            for vari in products:
                move_purchase = self.env['stock.move'].sudo().search([
                            ('product_id', '=', vari.id),
                            ('state','=','done'),
                            ('purchase_line_id.partner_id', '=', self.vendor_id.id), ('picking_code', '=', 'incoming')
                ])
                print('MOVe:::::::', move_purchase)

                move_sales_in = self.env['stock.move'].sudo().search([
                    ('product_id', '=', vari.id),
                    ('state', '=', 'done'),
                    ('sale_line_id', '!=', False), ('picking_code', '=', 'outgoing')
                ])
            
                
                for move in move_purchase:
                    total_qty_in = move.product_uom_qty
                    if total_qty_in > 0.0:
                        sales_per = move_sales_in.product_uom_qty / total_qty_in * 100
                    else:
                        sales_per = 0.0
                    data.append({
                        'vendor': self.vendor_id.name,
                        'product':move.name,
                        'avalible_qty':move.product_id.qty_available,
                        'qty': total_qty_in,
                        'sale_qty':move_sales_in.product_uom_qty,
                        'sales_per': sales_per,
                    })

########################################## List of Product witout select vendor ##########################################
        elif not self.vendor_id and self.type == 'per_product':
            for pro in product_ids:#self.product_id:
                if pro:  # Product None Variant
                    total_qty_in = 0.0
                    total_sale_qty = 0.0
                   
                    move_purchase = self.env['stock.move'].sudo().search([
                        ('product_id', '=', pro.id),
                        ('state', '=', 'done'),
                        ('purchase_line_id', '!=', False), ('picking_code', '=', 'incoming'),
                        ('purchase_line_id.partner_id.id', '!=', False)
                    ])
                    

                    move_sales_in = self.env['stock.move'].sudo().search([
                        ('product_id', '=', pro.id),
                        ('state', '=', 'done'),
                        ('sale_line_id', '!=', False), ('picking_code', '=', 'outgoing')
                    ])
                    for move in move_purchase:
                        total_qty_in += move.product_uom_qty
                        sales_per = 0.0
                        data.append(
                        {
                            'vendor': False,
                            'product': move.product_id.name,
                            'avalible_qty': move.product_id.qty_available,
                            'qty': total_qty_in,
                            'sale_qty': total_sale_qty,
                            'sales_per': round(sales_per, 2),
                        })

                    for sale in move_sales_in:
                        total_sale_qty += sale.product_uom_qty
                        if total_qty_in > 0.0:
                            sales_per = total_sale_qty / total_qty_in * 100
                        else:
                            sales_per = 0.0
                        data[0].update({
                            'sale_qty': total_sale_qty,
                            'sales_per': round(sales_per, 2),
                        })
        # list product by select Vendor
        elif self.vendor_id and self.type == 'per_product':
            for pro in product_ids:#self.product_id:
                if pro:  # Product None Variant
                    total_qty_in = 0.0
                    total_sale_qty = 0.0
                   
                    move_purchase = self.env['stock.move'].sudo().search([
                        ('product_id', '=', pro.id),
                        ('state', '=', 'done'),
                        ('purchase_line_id', '!=', False), ('picking_code', '=', 'incoming'),
                        ('purchase_line_id.partner_id.id', '=', self.vendor_id.id)
                    ])
                    

                    move_sales_in = self.env['stock.move'].sudo().search([
                        ('product_id', '=', pro.id),
                        ('state', '=', 'done'),
                        ('sale_line_id', '!=', False), ('picking_code', '=', 'outgoing')
                    ])
                    for move in move_purchase:
                        total_qty_in += move.product_uom_qty
                        sales_per = 0.0
                        data.append(
                        {
                            'vendor': self.vendor_id.name,
                            'product': move.product_id.name,
                            'avalible_qty': move.product_id.qty_available,
                            'qty': total_qty_in,
                            'sale_qty': total_sale_qty,
                            'sales_per': round(sales_per, 2),
                        })

                    for sale in move_sales_in:
                        total_sale_qty += sale.product_uom_qty
                        if total_qty_in > 0.0:
                            sales_per = total_sale_qty / total_qty_in * 100
                        else:
                            sales_per = 0.0
                        data[0].update({
                            'sale_qty': total_sale_qty,
                            'sales_per': round(sales_per, 2),
                        })
        
        # Total quantity stok move by vendor
        elif self.vendor_id:
            if self.type == 'per_vendor':
                total_qty_in = 0.00
                total_sale_qty = 0.00
                move_purchase = self.env['stock.move'].sudo().search([
                    ('picking_code', '=', 'incoming'),
                    ('state', '=', 'done'),
                    ('purchase_line_id.partner_id', '=', self.vendor_id.id)
                ])

                move_sales_in = self.env['stock.move'].sudo().search([
                    ('sale_line_id', '!=', False),('state','=','done'), ('picking_code', '=', 'outgoing')
                ])

                for move in move_purchase:
                    total_qty_in += move.product_uom_qty

                for sale in move_sales_in:
                    total_sale_qty += sale.product_uom_qty

                data.append(
                    {
                        'vendor': self.vendor_id.name,
                        'product':False,
                        'avalible_qty': False,
                        'qty': total_qty_in,
                        'sale_qty':False,
                        'sales_per':False,
                    })
        
        else:
            # Total quantity for all vendors:
            total_qty_in = 0.00
            total_sale_qty = 0.00
            partner = self.env['res.partner'].search([])
            move_purchase = self.env['stock.move'].sudo().search([
                ('picking_code', '=', 'incoming'),
                ('state', '=', 'done'),
                ('purchase_line_id.partner_id', 'in', partner.ids)
            ])

            move_sales_in = self.env['stock.move'].sudo().search([
                ('sale_line_id', '!=', False),('state','=','done'), ('picking_code', '=', 'outgoing')
            ])
            lst = []
            for mapp in move_purchase.mapped('purchase_line_id.partner_id'):
                total = 0.0
                for move in move_purchase:
                    if mapp == move.purchase_line_id.partner_id:
                        total += move.product_uom_qty
                data.append(
                {
                    'vendor': mapp.name,
                    'product':False,
                    'avalible_qty': False,
                    'qty': total,
                    'sale_qty':False,
                    'sales_per':False,
                })
           

                    
    
                        
               
                            
       
            
# ##########################Vendor And Type Selection
#         elif self.vendor_id and self.product_id:
#             for pro in self.product_id:
#                 if pro.product_variant_ids:
#                     total_qty_in = 0.0
#                     total_sale_qty = 0.0
#                     for var in pro.product_variant_ids:
#                         move_purchase = self.env['stock.move'].sudo().search([
#                             ('product_id', '=', var.id),
#                             ('state', '=', 'done'),
#                             ('purchase_line_id', '!=', False), ('picking_code', '=', 'incoming'),
#                             ('purchase_line_id.partner_id.id', '=', self.vendor_id.id)
#                         ])

#                         move_sales_in = self.env['stock.move'].sudo().search([
#                             ('product_id', '=', var.id),
#                             ('state', '=', 'done'),
#                             ('sale_line_id', '!=', False), ('picking_code', '=', 'outgoing')
#                         ])
#                         for move in move_purchase:
#                             total_qty_in += move.product_uom_qty

#                         for sale in move_sales_in:
#                             total_sale_qty += sale.product_uom_qty
#                     if total_qty_in > 0.0:
#                         sales_per = total_sale_qty / total_qty_in * 100
#                     else:
#                         sales_per = 0.0
#                     # avalible_qty = pro.qty_available
#                     data.append(
#                         {
#                             'vendor': self.vendor_id.name,
#                             'product': pro.name,
#                             'avalible_qty': pro.qty_available,
#                             'qty': total_qty_in,
#                             'sale_qty': total_sale_qty,
#                             'sales_per': round(sales_per, 2),
#                         })
#                 else:
#                     total_qty_in = 0.0
#                     total_sale_qty = 0.0
#                     move_purchase = self.env['stock.move'].sudo().search([
#                         ('product_id', '=', pro.id),
#                         ('state', '=', 'done'),
#                         ('purchase_line_id', '!=', False), ('picking_code', '=', 'incoming'),
#                         ('purchase_line_id.partner_id.id', '=', self.vendor_id.id)
#                     ])

#                     move_sales_in = self.env['stock.move'].sudo().search([
#                         ('product_id', '=', pro.id),
#                         ('state', '=', 'done'),
#                         ('sale_line_id', '!=', False), ('picking_code', '=', 'outgoing')
#                     ])
#                     for move in move_purchase:
#                         total_qty_in += move.product_uom_qty

#                     for sale in move_sales_in:
#                         total_sale_qty += sale.product_uom_qty
#                     if total_qty_in > 0.0:
#                         sales_per = total_sale_qty / total_qty_in * 100
#                     else:
#                         sales_per = 0.0
#                     avalible_qty = pro.qty_available
#                     data.append(
#                         {
#                             'vendor': self.vendor_id.name,
#                             'product': pro.name,
#                             'avalible_qty': avalible_qty,
#                             'qty': total_qty_in,
#                             'sale_qty': total_sale_qty,
#                             'sales_per': round(sales_per, 2),
#                         })
# ###########################################################################
#         elif self.vendor_id and not self.product_id:
#             if self.type == 'per_vendor':
#                 total_qty_in = 0.00
#                 total_sale_qty = 0.00
#                 move_purchase = self.env['stock.move'].sudo().search([
#                     ('picking_code', '=', 'incoming'),
#                     ('state', '=', 'done'),
#                     ('purchase_line_id.partner_id', '=', self.vendor_id.id)
#                 ])

#                 move_sales_in = self.env['stock.move'].sudo().search([
#                     ('sale_line_id', '!=', False),('state','=','done'), ('picking_code', '=', 'outgoing')
#                 ])

#                 for move in move_purchase:
#                     total_qty_in += move.product_uom_qty

#                 for sale in move_sales_in:
#                     total_sale_qty += sale.product_uom_qty

#                 data.append(
#                     {
#                         'vendor': self.vendor_id.name,
#                         'product':False,
#                         'avalible_qty': False,
#                         'qty': total_qty_in,
#                         'sale_qty':False,
#                         'sales_per':False,
#                     })
#             else:

#                 move_purchase = self.env['stock.move'].sudo().search([
#                     ('picking_code', '=', 'incoming'),
#                     ('state', '=', 'done'),
#                     ('purchase_line_id.partner_id', '=', self.vendor_id.id)
#                 ])

#                 move_sales_in = self.env['stock.move'].sudo().search([
#                     ('sale_line_id', '!=', False), ('state', '=', 'done'), ('picking_code', '=', 'outgoing')
#                 ])
#                 product_map = move_purchase.mapped('product_id')
#                 for pro in product_map:
#                     print('PO>>>>>>>>>', pro.product_template_variant_value_ids.ids)
#                     total_qty_in = 0.00
#                     total_sale_qty = 0.00
#                     avalible_qty = 0.00
#                     for move in move_purchase:
#                         if pro.id == move.product_id.id:
#                             total_qty_in += move.product_uom_qty
#                             avalible_qty += move.product_id.qty_available
#                             for sale in move_sales_in:
#                                 if pro.id == sale.product_id.id:
#                                     total_sale_qty += sale.product_uom_qty

#                     if total_qty_in > 0.0:
#                         sales_per = total_sale_qty / total_qty_in * 100
#                     else:
#                         sales_per = 0.0
#                     data.append(
#                         {
#                             'vendor': self.vendor_id.name,
#                             'product': pro.name,
#                             'avalible_qty': avalible_qty,
#                             'qty': total_qty_in,
#                             'sale_qty': total_sale_qty,
#                             'sales_per': round(sales_per, 2),
#                         })

        return data

   