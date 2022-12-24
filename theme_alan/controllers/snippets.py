# -*- coding: utf-8 -*-
import json
import datetime
import random
from datetime import timedelta

from odoo import http , _
from odoo.http import request
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteBlogSnippets(WebsiteBlog):

    @http.route(['/blog/get_blog_content'], type='http', auth='public', website=True, sitemap=False)
    def get_blog_content_data(self, **post):
        value={}
        if post.get('blog_config_id') != 'false' and post.get('blog_config_id'):
            collection_data=request.env['blog.configure'].browse(int(post.get('blog_config_id')))
            value.update({'blog_slider':collection_data})
        return request.render('theme_alan.blog_slider_content', value)

class WebsiteSaleSnippets(WebsiteSale):

    def get_slider_layout_design(self, style_id, values):
        """  Main method for get slider template"""
        template_id = request.env['product_slider_common.options'].sudo().browse(int(style_id)).get_external_id().get(
            int(style_id)) + '_template'
        template = request.env['ir.ui.view'].sudo().search(
            [('key', '=', template_id)])
        if template:
            response = http.Response(template=template_id, qcontext=values)
            return response.render()

    @http.route('/shop/get_product_snippet_content', type='json', auth='public', website=True)
    def get_product_snippet_content(self, **kwargs):
        """  get data For dynamic product slider """
        values = {}
        col_list = []
        if kwargs.get('collection_id'):
            add_to_cart = kwargs.get('add_to_cart', False)
            quick_view = kwargs.get('quick_view', False)
            pro_compare = kwargs.get('pro_compare', False)
            pro_wishlist = kwargs.get('pro_wishlist', False)
            pro_ribbon = kwargs.get('pro_ribbon', False)
            pro_ratting = kwargs.get('pro_ratting', False)
            current_filter_id = kwargs.get('current_filter_id', False)
            collection_list = kwargs.get('collection_id').split(',')
            slider_id = [int(i) for i in kwargs.get(
                'slider_type').split('_') if i.isdigit()]
            slider_type = request.env['product_slider.options'].sudo().browse(
                int(slider_id[0]))
            if(slider_id[0] == 0):
                return False
            tmplt_external_id = slider_type.get_external_id().get(slider_type.id) + '_template'
            tmplt = request.website.viewref(tmplt_external_id)
            current_filter = current_filter_id if not current_filter_id else request.env['slider_temp.collection.configure'].sudo().search([
                ('id', '=', int(current_filter_id))])
            for rec in collection_list:
                col_list.append(
                    # request.env['slider_temp.collection.configure'].sudo().browse(int(rec[0])))
                    request.env['slider_temp.collection.configure'].sudo().browse(int(rec)))
            if tmplt:
                values.update({
                    'slider': tmplt._render({
                        'add_to_cart': add_to_cart,
                        'quick_view': quick_view,
                        'pro_compare': pro_compare,
                        'pro_wishlist': pro_wishlist,
                        'pro_ribbon': pro_ribbon,
                        'pro_ratting': pro_ratting,
                        'slider_type': slider_type,
                        'collections': collection_list,
                        'col_list': tuple(col_list),
                        'check_default': False if current_filter_id else True,
                        'active_collection_data': int(current_filter) if current_filter else request.env['slider_temp.collection.configure'].browse(int(collection_list[0])).id,
                    })
                })
                return values
            else:
                return False
        return values

    @http.route('/shop/get_product_snippet_slider_view', type='json', auth='public', website=True)
    def get_product_snippet_slider_view(self, **kwargs):
        template_data = {
                         'slider_layout_1':'theme_alan.alan_slider_type_one_template',
                         'slider_layout_2':'theme_alan.alan_slider_type_two_template',
                         'slider_layout_3':'theme_alan.alan_slider_type_three_template',
                         'slider_layout_4':'theme_alan.alan_slider_type_four_template',
                         'slider_layout_5':'theme_alan.alan_slider_type_five_template',
                         'slider_layout_6':'theme_alan.alan_slider_type_six_template',
                         'slider_layout_7':'theme_alan.alan_slider_type_seven_template'
                        }

        collection_ids = kwargs.get('collection')
        if(not collection_ids):
            return False
        slider = kwargs.get('slider')
        template = template_data[slider]
        col_list = [request.env['slider_temp.collection.configure'].sudo().browse(int(rec))
                        for rec in collection_ids]
        context = {
            'for_preview':'true',
            'add_to_cart': 'true',
            'quick_view': 'true',
            'pro_compare': 'true',
            'pro_wishlist': 'true',
            'pro_ribbon': 'true',
            'pro_ratting': 'true',
            'collections': collection_ids,
            'slider_type': slider,
            'col_list': tuple(col_list),
            'check_default': 'true',
            'active_collection_data': request.env['slider_temp.collection.configure'].browse(int(collection_ids[0])).id,
            }
        get_products_temp = request.env['ir.ui.view']._render_template(
                            template,context)
        return {'config_preview':get_products_temp}

    @http.route('/shop/get_product_variant_snippet_content', type='json', auth='public', website=True)
    def get_product_variant_snippet_content(self, **kwargs):
        """  get data For dynamic product variant slider """
        values = {}
        col_list = []
        if kwargs.get('collection_id'):
            add_to_cart = kwargs.get('add_to_cart', False)
            quick_view = kwargs.get('quick_view', False)
            pro_compare = kwargs.get('pro_compare', False)
            pro_wishlist = kwargs.get('pro_wishlist', False)
            pro_ribbon = kwargs.get('pro_ribbon', False)
            pro_ratting = kwargs.get('pro_ratting', False)
            current_filter_id = kwargs.get('current_filter_id', False)
            collection_list = kwargs.get('collection_id').split(',')
            slider_id = [int(i) for i in kwargs.get(
                'slider_type').split('_') if i.isdigit()]
            slider_type = request.env['product_var_slider.options'].sudo().browse(
                int(slider_id[0]))
            if(slider_id[0] == 0):
                return False
            tmplt_external_id = slider_type.get_external_id().get(slider_type.id) + '_template'
            tmplt = request.website.viewref(tmplt_external_id)
            current_filter = current_filter_id if not current_filter_id else request.env['slider_var.collection.configure'].sudo().search([
                ('id', '=', int(current_filter_id))])
            for rec in collection_list:
                col_list.append(
                    request.env['slider_var.collection.configure'].sudo().browse(int(rec[0])))
            if tmplt:
                values.update({
                    'slider': tmplt._render({
                        'add_to_cart': add_to_cart,
                        'quick_view': quick_view,
                        'pro_compare': pro_compare,
                        'pro_wishlist': pro_wishlist,
                        'pro_ribbon': pro_ribbon,
                        'pro_ratting': pro_ratting,
                        'slider_type': slider_type,
                        'collections': collection_list,
                        'col_list': tuple(col_list),
                        'check_default': False if current_filter_id else True,
                        'active_collection_data': int(current_filter) if current_filter else request.env['slider_var.collection.configure'].browse(int(collection_list[0])).id,
                    })
                })
                return values
            else:
                return False
        return values

    @http.route('/shop/get_product_variant_snippet_slider_view', type='json', auth='public', website=True)
    def get_product_variant_snippet_slider_view(self, **kwargs):
        template_data = {

                         'slider_layout_1':'theme_alan.alan_slider_type_one_variant_template',
                         'slider_layout_2':'theme_alan.alan_slider_type_two_variant_template',
                         'slider_layout_3':'theme_alan.alan_slider_type_three_variant_template',
                         'slider_layout_4':'theme_alan.alan_slider_type_four_variant_template',
                         'slider_layout_5':'theme_alan.alan_slider_type_five_variant_template',
                         'slider_layout_6':'theme_alan.alan_slider_type_six_variant_template',
                         'slider_layout_7':'theme_alan.alan_slider_type_seven_variant_template'
                        }

        collection_ids = kwargs.get('collection')
        if(not collection_ids):
            return False
        slider = kwargs.get('slider')
        template = template_data[slider]
        col_list = [request.env['slider_var.collection.configure'].sudo().browse(int(rec))
                        for rec in collection_ids]
        context = {
            'for_preview':'true',
            'add_to_cart': 'true',
            'quick_view': 'true',
            'pro_compare': 'true',
            'pro_wishlist': 'true',
            'pro_ribbon': 'true',
            'pro_ratting': 'true',
            'collections': collection_ids,
            'slider_type': slider,
            'col_list': tuple(col_list),
            'check_default': 'true',
            'active_collection_data': request.env['slider_var.collection.configure'].browse(int(collection_ids[0])).id,
            }
        get_products_temp = request.env['ir.ui.view']._render_template(
                            template,context)
        return {'config_preview':get_products_temp}


    @http.route(['/get_prod_quick_view_details'], type='json', auth='public', website=True)
    def get_prod_quick_view_details(self, **kw):
        """  get data for product slider quick view  """
        product_id = int(kw.get('prod_id', 0))
        if product_id > 0:
            product = http.request.env['product.template'].sudo().search(
                [('id', '=', product_id)])
            pricelist = request.website.get_current_pricelist()
            from_currency = request.env.user.company_id.currency_id
            to_currency = pricelist.currency_id

            def compute_currency(price): return from_currency.compute(
                price, to_currency)
            return request.env.ref('atharva_theme_base.as_product_quick_view_holder')._render({
                'product': product,
                'compute_currency': compute_currency or None})
        else:
            return request.env.ref('atharva_theme_base.as_product_quick_view_holder')._render({
                'error': _('There is some problem with this product.!')
            })

    @http.route(['/get_best_seller_product_data'], type='json', auth='public', website=True)
    def get_best_seller_product_data(self, **kwargs):
        """  get data For best seller dynamic product slider """
        style_id = kwargs.get('style_id', False)
        website_id = request.website.id
        request.env.cr.execute("""SELECT PT.id, SUM(SO.product_uom_qty),PT.website_id
                                  FROM sale_order S
                                  JOIN sale_order_line SO ON (S.id = SO.order_id)
                                  JOIN product_product P ON (SO.product_id = P.id)
                                  JOIN product_template pt ON (P.product_tmpl_id = PT.id)
                                  WHERE S.state in ('sale','done')
                                  AND (S.date_order >= %s AND S.date_order <= %s)
                                  AND (PT.website_id IS NULL OR PT.website_id = %s)
                                  AND PT.active='t'
                                  AND PT.is_published='t'
                                  GROUP BY PT.id
                                  ORDER BY SUM(SO.product_uom_qty)
                                  DESC LIMIT %s
                               """, [datetime.datetime.today() - timedelta(8), datetime.datetime.today(), website_id, 8])
        table = request.env.cr.fetchall()
        products = []
        for record in table:
            if record[0]:
                pro_obj = request.env[
                    'product.template'].sudo().browse(record[0])
                if pro_obj.sale_ok == True and pro_obj.is_published == True:
                    products.append(pro_obj)
        if products:
            values = {
                'products': products,
                'section_title': 'Best Seller Product Slider'
            }
            slider_layout_data = self.get_slider_layout_design(
                style_id, values)
            return slider_layout_data

    @http.route(['/get_latest_product_data'], type='json', auth='public', website=True)
    def get_latest_product_data(self, **kwargs):
        """  get data For latest products dynamic slider """
        style_id = kwargs.get('style_id', False)
        products = request.env['product.template'].sudo().search(
            [('website_published', '=', True),('sale_ok', '=', True),('is_published','=',True)], order='id desc', limit=10)
        if products:
            values = {
                'products': products,
                'section_title': 'Latest Products Slider'
            }
            slider_layout_data = self.get_slider_layout_design(
                style_id, values)
            return slider_layout_data

    @http.route(['/get_category_products_data'], type='json', auth='public', website=True)
    def get_category_products_data(self, **kwargs):
        """  get data For category wise dynamic product slider """
        style_id = kwargs.get('style_id', False)
        category_ids = kwargs.get('category_ids', False)
        category_ids = category_ids.split(',')

        domain = [('public_categ_ids', 'in', category_ids),
                  ('website_published', '=', True),('sale_ok', '=', True),('is_published','=',True)]
        products = request.env['product.template'].sudo().search(domain)

        if products:
            values = {
                'products': products,
                'section_title': 'Category Products Slider'
            }
            slider_layout_data = self.get_slider_layout_design(
                style_id, values)
            return slider_layout_data

    @http.route(['/get_brand_products_data'], type='json', auth='public', website=True)
    def get_brand_products_data(self, **kwargs):
        """  get data For brand wise dynamic product slider """
        style_id = kwargs.get('style_id', False)
        brand_ids = kwargs.get('brand_ids', False)
        if brand_ids:
            brand_ids = brand_ids.split(',')
            for i in range(0, len(brand_ids)):
                brand_ids[i] = int(brand_ids[i])

            domain = [('product_brand_id.id', 'in', brand_ids),
                      ('website_published', '=', True),('sale_ok', '=', True),('is_published','=',True)]
            products = request.env['product.template'].sudo().search(domain)
            if products:
                values = {
                    'products': products,
                    'section_title': 'Brands Products Slider'
                }
                slider_layout_data = self.get_slider_layout_design(
                    style_id, values)
                return slider_layout_data

    @http.route(['/shop/get_brand_snippet_content'], type='json', auth='public', website=True)
    def get_brand_snippet_content(self, **kwargs):
        """  get data For product brand slider """
        values = {}
        if kwargs.get('collection_id') and kwargs.get('collection_id') != 'false':
            collection_data = request.env['slider_brand.collection.configure'].browse(
                int(kwargs.get('collection_id')))
            if collection_data and collection_data.active:
                values.update({
                    'auto_slider_value': collection_data.auto_slider,
                    'slider_timing': collection_data.slider_time * 1000,
                    'item_count': int(collection_data.item_count),
                })
                slider_type = collection_data.slider_layout_option_id
                tmplt_external_id = collection_data.slider_layout_option_id.get_external_id(
                ).get(collection_data.slider_layout_option_id.id) + '_template'
                tmplt = request.website.viewref(tmplt_external_id)
                if tmplt:
                    values.update({
                        'slider': tmplt._render({
                            'slider_type': slider_type,
                            'obj': collection_data
                        })
                    })
                    return values
                else:
                    return False
            else:
                values.update({
                    'disable_group': 'True'
                })
        return values

    @http.route(['/shop/get_category_snippet_content'], type='json', auth='public', website=True)
    def get_category_snippet_content(self, **kwargs):
        """  get data For product e-commerce category slider """
        values = {}
        if kwargs.get('collection_id') and kwargs.get('collection_id') != 'false':
            collection_data = request.env['slider_cat.collection.configure'].browse(
                int(kwargs.get('collection_id')))
            if collection_data and collection_data.active:
                slider_type = collection_data.slider_layout_option_id
                tmplt_external_id = collection_data.slider_layout_option_id.get_external_id(
                ).get(collection_data.slider_layout_option_id.id) + '_template'
                tmplt = request.website.viewref(tmplt_external_id)
                if tmplt:
                    values.update({
                        'slider': tmplt._render({
                            'slider_type': slider_type,
                            'obj': collection_data
                        })
                    })
                    return values
                else:
                    return False
            else:
                values.update({
                    'disable_group': 'True'
                })
        return values

    @http.route(['/get_website_faq_list'], type='json', auth='public', website=True)
    def get_website_faq_list(self):
        """ get data for FAQ slider template """
        response = http.Response(template='atharva_theme_base.as_dynamic_faq_container')
        return response.render()

    @http.route('/get/product_banner/',type='json',auth='public',website=True)
    def get_special_product(self, **post):
        id_list = post.get('id').split(',')
        if(post.get('edit_mode') == True):
            if(len(id_list) != 0):
                product_list = [request.env['product.template'].sudo().browse(int(i)) for i in id_list if i != '']
                prod_name = ""
                for i in product_list:
                    prod_name += i.name + ','
                return {'prod_list':prod_name}
            else:
                return {'prod_list':'NO PRODUCT SELECTED'}
        else:
            get_product_list = [request.env['product.template'].sudo().browse(int(i)) for i in id_list if i != '' ]
            context = { 'products':get_product_list,'add_to_cart':post.get('add_to_cart'),
                        'prod_rating':post.get('prod_rating'),
                        'prod_label':post.get('prod_label'),
                        'buy_btn':post.get('buy_btn'),
                        'pos':post.get('pos')
                    }
            get_products_temp = request.env['ir.ui.view']._render_template(
                            'theme_alan.as_product_banner_slider_front_template',context)
        return {'prods_banner_temp':get_products_temp}

    @http.route('/get/all_product/',type='json',auth='public',website=True)
    def get_all_product(self):
        getproduct = request.env['product.template'].sudo().search([('sale_ok', '=', True),('is_published','=',True)])
        prod_list = [{'id':i.id,'text':i.name,'image_url':request.website.image_url(i, 'image_512')} for i in getproduct]
        return prod_list

    @http.route('/get/product_detail/',type="json",auth='public',website=True)
    def get_product_name(self,**kwargs):
        prod_id = int(kwargs.get('id'))
        getpd = request.env['product.template'].sudo().search([('id','=',prod_id)])
        if(kwargs.get('name_only') == True):
            return getpd.name
        elif(kwargs.get('popover') == True):
            get_products_temp = request.env['ir.ui.view']._render_template(
                    'theme_alan.img_hotspot_template',{'product':getpd,'cls':kwargs.get('popstyle')})
            return get_products_temp
        return True

    @http.route('/get/quick_add_to_cart' ,type='json',auth='public',website=True)
    def quick_add_to_cart(self,**kw):
        getProd = request.env['product.template'].sudo().search([('id','=',kw['prodId'])])
        get_template = request.env['ir.ui.view']._render_template('theme_alan.quick_cart', {'product':getProd})
        return {'template':get_template}


    @http.route('/quick_update_cart' ,type='json',auth='public',website=True)
    def quick_update_cart(self,**kw):
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        add_qty = 1
        if kw.get('varient', True):
            for i in kw['formVals']:
                if(i['name'] == 'add_qty'):
                    add_qty = int(i['value'])
                    break
            value = sale_order._cart_update(
                product_id=int(kw['formVals'][1]['value']),
                add_qty=add_qty,
                set_qty=0,
                product_custom_attribute_values=kw['customVals'],
                no_variant_attribute_values=[]
            )
            data = {'add_qty':add_qty, 'prod_temp_id':kw['formVals'][2]['value']}
            if "warning" in value.keys():
                data['warning'] = value["warning"]
            else:
                data['warning'] = False
            return data
        else:
            value = sale_order._cart_update(
                product_id=kw['prod_varient_id'],
                add_qty=add_qty,
                set_qty=0,
                product_custom_attribute_values=[],
                no_variant_attribute_values=[]
            )
            data = {'add_qty':add_qty, 'prod_temp_id':kw['product_temp_id']}
            if "warning" in value.keys():
                data['warning'] = value["warning"]
            else:
                data['warning'] = False
            return data

    @http.route('/quick_suggestion_and_notifier' ,type='json',auth='public',website=True)
    def quick_suggestion_and_cart_notifier(self, **kw):
        getProd = request.env['product.template'].sudo().search([('id','=',kw['prod_id'])])
        altern_prods = getProd.alternative_product_ids
        access_prods = getProd.accessory_product_ids
        prod_sugge_list = []
        for prod in altern_prods:
            prod_sugge_list.append(prod)
        for prod in access_prods:
            prod_sugge_list.append(prod)
        random.shuffle(prod_sugge_list)
        prod_sugge_list = prod_sugge_list[:6]
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        total_cart_item = 0
        for line in order.order_line:
            total_cart_item += line.product_uom_qty
        response = {'cart_product':getProd,'total_cart_item':int(total_cart_item),'order':order,'suggest_prod':prod_sugge_list,
        'prod_image':request.website.image_url(getProd, 'image_1920')}
        get_template = request.env['ir.ui.view']._render_template('theme_alan.quick_cart_detail_and_suggestion', response)
        return {'template':get_template}