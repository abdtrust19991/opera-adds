# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)

class picking(models.Model):
    _inherit = 'stock.picking'


    def button_validate(self):
        rec = super(picking, self).button_validate()
        print("purchase_id ==>", self.purchase_id)
        if self.purchase_id:
            self.purchase_id.check_plan(type='picking')
        return rec



class purchase_order(models.Model):
    _inherit = 'purchase.order'

    link_plan = fields.Boolean(string="Link With Plan",  )
    plan_id = fields.Many2one(comodel_name="purchase.plan", string="Purchase Plan", required=False,domain="[('state', '=', 'run')]" )

    def get_color(self,plan_id):
        lst_color=[]
        lst_factory = []
        fact = []
        c = defaultdict(int)
        lst_temp=[]
        lst_co=[]
        lst = defaultdict(int)
        res = self.env['purchase.order'].search([('plan_id','=',plan_id)])
        for rec in res:
            for line in rec.order_line:
                if line.color:
                    if line.product_id.product_tmpl_id.id not in lst_temp or line.color.name not in lst_co:
                        co={
                            'color':line.color.name,
                            'No':1,
                        }
                        lst_temp.append(line.product_id.product_tmpl_id.id)
                        lst_co.append(line.color.name)
                        lst_color.append(co)
                if line.factory:
                    res={
                        'factory':line.factory.name,
                        'amount':line.price_subtotal,
                        'qty':line.product_qty,
                        'model_qty':line.model_no,
                        'templ':line.product_id.product_tmpl_id.id,
                    }
                    lst_factory.append(res)

        if lst_factory:

            fact =[{'factory':lst_factory[0]['factory'],'amount':0.0,'qty':0.0,'model_qty':0}]
            pro_lst=[]
            for d in lst_factory:

                flag = False
                for f in fact:
                    if d['factory'] == f['factory']:
                        f['amount'] += d['amount']
                        f['qty'] += d['qty']
                        f['templ'] = d['templ']
                        if f['templ'] not in pro_lst:
                            pro_lst.append(f['templ'])
                            f['model_qty'] += 1

                        flag =False
                        break
                    else:
                        flag=True
                if flag:
                    fact.append(d)
        if lst_color:
            for co in lst_color:
                lst[co['color']] += co['No']
        lst_color =[{'name': name, 'num': qty} for name, qty, in lst.items()]

        return {'color':lst_color,'factory':fact}
    def check_plan(self,type='po'):
        for order in self:
            if type == 'po':
                if order.link_plan:
                    categ_ids = []
                    for line in order.order_line:
                        for rec in order.plan_id.plan_line_ids:

                            print("hhhh 2*** ", rec.category_id)
                            if line.product_id.categ_id.id == rec.category_id.id:
                                print("qty_received 1*** ",line.qty_received)
                                if line.product_id.categ_id.id not in categ_ids:
                                    categ_ids.append(line.product_id.categ_id.id)
                                rec.a_qty += line.product_qty
                                rec.rec_qty += line.qty_received
                                rec.a_total += line.product_qty * line.price_unit
                                rec.a_cost = rec.a_total / rec.a_qty
                                break

                    for group in order.plan_id.plan_line_ids:
                        if group.category_id.id in categ_ids:
                            group.a_model_no += 1
                    lst_data = self.get_color(self.plan_id.id)
                    print("lst_data =>", lst_data)
                    co_ids = []
                    fact_ids = []
                    if lst_data:
                        if lst_data['color']:
                            for co in lst_data['color']:
                                print('co ==> ', co)
                                co = self.env['plan.color.line'].create(co)
                                co_ids.append(co.id)
                        if lst_data['factory']:
                            for fact in lst_data['factory']:
                                print('fact ==> ', fact)
                                val = fact
                                val['average'] = round(fact['amount'] / fact['qty'], 2)
                                print('**** val = ', val)
                                f = self.env['plan.factory.line'].create(val)
                                fact_ids.append(f.id)
                    self.plan_id.write({'plan_color_ids': [(6, 0, co_ids)], 'plan_factory_ids': [(6, 0, fact_ids)]})

                    # print("lst_data =>",lst_data.stop)
            if type == 'picking':
                if order.link_plan:
                    categ_ids = []
                    for line in order.order_line:
                        for rec in order.plan_id.plan_line_ids:
                            if line.product_id.categ_id.id == rec.category_id.id:
                                rec.rec_qty += line.qty_received
                                break



    def button_confirm(self):
        print("hhhh *** 111")
        self.check_plan()
        return super(purchase_order, self).button_confirm()

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    model_no = fields.Integer(string="Model Number", required=False,readonly=True,states={'purchase ': [('readonly', True)]}, default=1 )
    color = fields.Many2one(comodel_name="color.code", string="Color",states={'purchase': [('readonly', True)]},  required=False, )
    factory = fields.Many2one(comodel_name="factory.code", string="Factory", states={'purchase': [('readonly', True)]}, required=False, )
    categ_id = fields.Many2one(comodel_name="product.category", related="product_id.categ_id", string="Category", required=False, )
    barcode = fields.Char(string="Barcode", related="product_id.barcode", required=False, )


    @api.onchange('product_id')
    def onchange_product_id(self):
        super(purchase_order_line, self).onchange_product_id()
        if self.order_id.plan_id:
            lst_plan=[]
            for line in self.order_id.plan_id.plan_line_ids:
                lst_plan.append(line.category_id.id)
            print("fff*** kk",lst_plan)

            if self.product_id:
                if self.product_id.categ_id.id not in lst_plan:
                    print("fff*** kk 88 11 ",self.product_id.id )
                    raise ValidationError("The Category of this product not exist in Purchase Plan")
                    # _logger.warning("this product not exist in purchase Plan")

class color_code(models.Model):
    _name = 'color.code'

    name = fields.Char("Color Name",  required=True)
class factory_code(models.Model):
    _name = 'factory.code'

    name = fields.Char("Factory Name",  required=True)





