# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _




class purchase_plan(models.Model):
    _name = 'purchase.plan'
    _rec_name = 'number'

    name = fields.Char("Name",)
    number = fields.Char("Number",readonly=True)
    plan_lines = fields.One2many(comodel_name="purchase.plan.line", inverse_name="plan_id", string="Plan Lines", required=False, )

    plan_line_ids = fields.One2many(comodel_name="purchase.plan.line",inverse_name="plan_id", string="Plan Lines", required=True)
    actual_line_ids = fields.One2many(comodel_name="purchase.plan.line",inverse_name="plan_id",  string="Actual Lines",readonly=True )
    diff_line_ids = fields.One2many(comodel_name="purchase.plan.line",inverse_name="plan_id",  string="Difference Lines",readonly=True )
    rat_line_ids = fields.One2many(comodel_name="purchase.plan.line",inverse_name="plan_id",  string="Ratio Lines", readonly=True)
    recive_line_ids = fields.One2many(comodel_name="purchase.plan.line",inverse_name="plan_id",  string="Receive Lines", readonly=True)

    plan_color_ids = fields.Many2many(comodel_name="plan.color.line", string="Colors", readonly=True)
    plan_factory_ids = fields.Many2many(comodel_name="plan.factory.line", string="Factories", readonly=True)
    date = fields.Date(string="Date",default=fields.Date.context_today)
    active = fields.Boolean(string="Active", default=True )
    count_purchase = fields.Integer(string="", required=False,compute="_compute_count_purchase" )
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('run', 'Running'),('close', 'Closed'), ],default="draft", required=False, )



    def action_confirm(self):
        self.state='run'
    def action_close(self):
        self.state='close'



    def name_get(self):
        result = []
        for rec in self:
            if rec.name:
                name = rec.name +' [ ' + rec.number + ' ]'
            if not rec.name and rec.number :
                name = rec.number
            result.append((rec.id,name))
        return result

    def _compute_count_purchase(self):
        for rec in self:
            orders = self.env['purchase.order'].search([('plan_id', '=', rec.id)])
            self.count_purchase = len(orders.ids)

    def action_open_purchase(self):
        for rec in self:
            orders = self.env['purchase.order'].search([('plan_id', '=', rec.id)])
            domain = [('id', 'in', orders.ids)]
            view_tree = {
                'name': _(' Purchase Order '),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                'domain': domain,
                'readonly': True,
            }
            return view_tree
    def toggle_active(self):

        self.active = not self.active

    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'purchase.plan'
        datas['form'] = self.read()[0]
        print("datas['form']",datas['form'])
        print("datas['model']",datas['model'])
        print("datas['ids']",datas['ids'])
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        print("datas", datas)
        print("context", context)

        print("context 11", context)
        return self.env.ref('purchase_plan.purchase_plan_xlsx').report_action(self, data=datas)

    @api.model
    def create(self, vals):

        vals['number'] = self.env['ir.sequence'].next_by_code('pur.plan')
        return super(purchase_plan, self).create(vals)


class purchase_plane_line(models.Model):
    _name = 'purchase.plan.line'


    category_id = fields.Many2one(comodel_name="product.category", string="Group", required=True, )
    plan_id = fields.Many2one(comodel_name="purchase.plan", string="Plan",  )
    p_model_no = fields.Integer(string="P-Model", required=True, )
    p_cost = fields.Float(string="P-UnitCost",  required=True, )
    p_qty = fields.Float(string="P-QTY",  required=True, )
    p_total = fields.Float(string="P-Amount",  required=False,compute="_compute_total" ,store=True)
    a_model_no = fields.Integer(string="A-Model", required=False, readonly=True,store=True)
    a_cost = fields.Float(string="A-UnitCost", required=False, readonly=True,store=True)
    a_qty = fields.Float(string="A-QTY", required=False,readonly=True,store=True )
    a_total = fields.Float(string="A-Amount", required=False,readonly=True,store=True )
    dif_qty = fields.Float(string="DIF-QTY", required=False,compute="_compute_difference" ,store=True)
    dif_total = fields.Float(string="DIF-Amount", required=False, compute="_compute_difference",store=True)
    dif_model = fields.Float(string="DIF-Model", required=False, compute="_compute_difference",store=True)
    rat_qty = fields.Float(string="Rat-QTY", required=False,compute="_compute_difference",store=True )
    rec_qty = fields.Float(string="Rec-QTY", required=False,)

    rat_total = fields.Float(string="Rat-Amount", required=False,compute="_compute_difference" ,store=True )
    rat_model = fields.Float(string="Rat-Model", required=False,compute="_compute_difference",store=True  )




    @api.depends('p_cost','p_qty','a_cost','a_qty','a_model_no','p_model_no')
    def _compute_total(self):
        self.p_total=self.p_cost * self.p_qty


    @api.depends('p_cost','p_qty','a_cost','a_qty','p_total','a_total','a_model_no','p_model_no')
    def _compute_difference(self):
        self.dif_qty = self.p_qty - self.a_qty
        self.dif_total = self.p_total - self.a_total
        self.dif_model = self.p_model_no - self.a_model_no
        rat_total = 0.0
        if self.a_total > 0.0 and self.p_total > 0.0:
            rat_total = self.a_total / self.p_total * 100
        self.rat_total = round(rat_total,2)
        rat_qty = 0.0
        if self.a_qty > 0.0 and self.p_qty > 0.0:
            rat_qty = self.a_qty / self.p_qty * 100
        self.rat_qty = round(rat_qty, 2)

        rat_model = 0.0
        if self.a_model_no > 0.0 and self.p_model_no > 0.0:
            rat_model = self.a_model_no / self.p_model_no * 100
        self.rat_model = round(rat_model, 2)




class plan_color_line(models.Model):
    _name = 'plan.color.line'

    name = fields.Char("Color")
    num = fields.Char("No")

class factory_color_line(models.Model):
    _name = 'plan.factory.line'

    factory = fields.Char("Factory")
    amount = fields.Char("amount")
    qty = fields.Char("Qty")
    model_qty = fields.Char("Qty-Model")
    average = fields.Char("Average")
    templ = fields.Many2one(comodel_name="product.template", string="Product", required=False, )

