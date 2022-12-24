# -*- coding: utf-8 -*-

import json
import math
import logging
import werkzeug
from werkzeug.exceptions import NotFound

import odoo
from odoo import http , _
from odoo.http import request
from odoo.osv import expression
from odoo.exceptions import UserError

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_oauth.controllers.main import OAuthLogin
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """ Override for shop method """
        rating = post.get('rating')
        max_val = min_val = 0
        custom_min_val = custom_max_val = 0
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4
        product_ids = request.env['product.template'].search(
            ['&', ('sale_ok', '=', True), ('active', '=', True)])

        if product_ids and product_ids.ids:
            request.cr.execute(
                'select min(list_price),max(list_price) from product_template where id in %s', (tuple(product_ids.ids),))
            min_max_vals = request.cr.fetchall()
            min_val = min_max_vals[0][0] or 0
            if int(min_val) == 0:
                min_val = 1
            max_val = min_max_vals[0][1] or 1
            if post.get('min_val') and post.get('max_val'):
                custom_min_val = float(post.get('min_val'))
                custom_max_val = float(post.get('max_val'))
                post.update(
                    {'attrib_price': '%s-%s' % (custom_min_val, custom_max_val)})
            else:
                post.update({'attrib_price': '%s-%s' % (min_val, max_val)})


        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split('-')]
                         for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        if post.get('min_val') and post.get('max_val'):
            domain += [('list_price', '>=', float(post.get('min_val'))),
                       ('list_price', '<=', float(post.get('max_val')))]

        brand_ids = []
        brand = post.get('brand')

        brand_list = request.httprequest.args.getlist('brand')
        if brand:
            brand_values = [[str(x) for x in v.rsplit('-', 1)]
                            for v in brand_list if v]
            brand_ids = list(set([int(v[1]) for v in brand_values]))
            if len(brand_ids) > 0:
                domain += [('product_brand_id', 'in', brand_ids)]

        tag_list = request.httprequest.args.getlist('tags')
        tag_ids = []
        tag_values = []
        if post.get('tags'):
            tag_values = [[str(x) for x in v.split('-')]
                         for v in tag_list if v]
            tag_ids = list(set([int(v[1]) for v in tag_values]))
            if len(tag_ids) > 0:
                domain += [('product_tags_ids', 'in', tag_ids)]

        keep = QueryURL('/shop', category=category and int(category),
                        search=search, attrib=attrib_list, tags=tag_list, order=post.get('order')
                        ,brand=post.get('brand'),rating=post.get('rating'),min_val=post.get('min_val')
                        ,max_val=post.get('max_val'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(
            request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = '/shop'
        if search:
            post['search'] = search
        if attrib_list:
            post['attrib'] = attrib_list
        if tag_list:
            post['tags'] = tag_list

        Product = request.env['product.template'].with_context(bin_size=True)

        order = http.request.website.sale_get_order()
        if order and order.state != 'draft':
            http.request.session['sale_order_id'] = None
            order = http.request.website.sale_get_order()

        if rating != None:
            domain = expression.AND([[('product_rating','>=',rating)], domain])
        search_product = Product.search(domain)
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        issubcategory = False

        if category:
            if(len(category.parent_id) != 0):
                issubcategory = category
            url = '/shop/category/%s' % slug(category)

        product_count = len(search_product)

        pager = request.website.pager(
            url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(
            domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search(
                [('product_tmpl_ids', 'in', search_product.ids)])
            brands = request.env['as.product.brand'].sudo().search(
                [('active', '=', True), ('website_id', 'in', (False, request.website.id)), ('brand_product_ids', 'in', search_product.ids)])

        else:
            attributes = ProductAttribute.browse(attributes_ids)
            brands = request.env['as.product.brand'].sudo().search(
                    [('active', '=', True), ('website_id', 'in', (False, request.website.id)),('id','in',brand_ids)])
        tags = request.env['product.tags'].search([('active','=',True)])

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        attr_value_count = {}
        brand_count = {}
        tag_count = {}
        rating_count = {}

        prod_lst = Product.search(domain, limit=False, order=self._get_search_order(post))
        attrs_line = request.env['product.template.attribute.line'].search([('product_tmpl_id','in',prod_lst.ids)])

        if request.website.viewref('atharva_theme_base.product_count_on_filter').active:
            for attr in attributes:
                for val in attr.value_ids:
                    attr_value_count[val.id] = 0

            if attrs_line:
                for each_line in attrs_line:
                    for val in each_line.value_ids:
                        if val.id in attr_value_count:
                            attr_value_count[val.id] += 1

            tag_count = { tag.id : 0 for tag in tags }
            rating_count = { r : 0 for r in range(1,5) }
            rat_lst = [1,2,3,4]

            for r in search_product:
                if r.product_brand_id.id in brand_count:
                    brand_count[r.product_brand_id.id] += 1
                else:
                    if r.product_brand_id:
                        brand_count[r.product_brand_id.id] = 1

                if r.product_tags_ids:
                    for tag in r.product_tags_ids:
                        if tag.id in tag_count:
                            tag_count[tag.id] += 1

                for rat in rat_lst:
                    if r.product_rating >= rat:
                        rating_count[rat] += 1

        hide_tag = {}
        hide_rating = {}
        hide_attr_value = {}
        hide_tag_len = 1
        hide_rating_len = 1
        hide_attr_value_len = 1

        if request.website.viewref('atharva_theme_base.hide_no_match_attr').active:
            hide_tag = { tag.id : 0 for tag in tags }
            hide_tag_len = len(hide_tag)
            hide_rating = { r : 0 for r in range(1,5) }
            hide_rating_len = len(hide_rating)
            rat_lst = [1,2,3,4]

            for attr in attributes:
                for val in attr.value_ids:
                    hide_attr_value[val.id] = 0

            hide_attr_value_len = len(hide_attr_value)

            if attrs_line:
                for each_line in attrs_line:
                    for val in each_line.value_ids:
                        if val.id in hide_attr_value:
                            del hide_attr_value[val.id]

            for r in search_product:
                if r.product_tags_ids:
                    for tag in r.product_tags_ids:
                        if tag.id in hide_tag:
                            del hide_tag[tag.id]

                for rat in rat_lst:
                    if r.product_rating >= rat:
                        if rat in hide_rating:
                            del hide_rating[rat]

        values = {
            'search': search,
            'category': category,
            'is_subcatetgory':issubcategory,
            'attrib_list': attrib_list,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'product_order':post.get('order'),
            'pager': pager,
            'rating':rating,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'tags':tags,
            'tag_list':tag_list,
            'tag_set':tag_ids,
            'sel_brand': brand,
            'brands': brands,
            'brand_set': brand_ids,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'min_val': min_val,
            'max_val': max_val,
            'custom_min_val': custom_min_val,
            'custom_max_val': custom_max_val,
            'floor': math.floor,
            'ceil': math.ceil,
            'website_sale_order': order,
            'attr_value_count':attr_value_count,
            'brand_count':brand_count,
            'tag_count':tag_count,
            'rating_count':rating_count,
            'hide_tag':hide_tag,
            'hide_rating':hide_rating,
            'hide_rating_len':hide_rating_len,
            'hide_attr_value':hide_attr_value,
            'hide_tag_len':hide_tag_len,
            'hide_attr_value_len':hide_attr_value_len
        }
        if category:
            values['main_object'] = category
        return request.render('website_sale.products', values)

    @http.route('/json/shop/product/', type='json', auth='public', website=True, sitemap=False)
    def get_next_product(self,page,ppg,category_id=None,search=None,**post):
        rating = post.get('rating')
        if(post.get('previous') != None):
            page = int(page) - 1
        else:
            page = int(page) + 1
        Category = request.env['product.public.category']
        if category_id:
            category = Category.search([('id', '=', int(category_id))], limit=1)
            if not category or not category.can_access_from_current_website():
                return False
        else:
            category = Category
        order = http.request.website.sale_get_order()

        if order and order.state != 'draft':
            http.request.session['sale_order_id'] = None
            order = http.request.website.sale_get_order()

        ppr = request.env['website'].get_current_website().shop_ppr or 4
        attrib_values= post.get('attrval')
        attrib_values = json.loads(attrib_values)
        attrib_list = [str(i[0]) + "-" + str(i[1]) for i in attrib_values]

        realpost = {}
        if(len(attrib_values) != 0):
            realpost['attrib'] = attrib_list

        domain = self._get_search_domain(search, category, attrib_values)
        if post.get('min_val') != '0' and post.get('max_val') != '0':
            domain += [('list_price', '>=', float(post.get('min_val'))),
                       ('list_price', '<=', float(post.get('max_val')))]
            realpost['min_val'] = int(json.loads(post.get('min_val')))
            realpost['max_val'] = int(json.loads(post.get('max_val')))

        if post.get('brand_ids'):
            brand_ids = json.loads(post.get('brand_ids'))
            if(len(brand_ids) > 0):
                domain += [('product_brand_id', 'in', brand_ids)]
                get_brand_url = request.env['as.product.brand'].search([('id','=',brand_ids[0])])
                brandurl = get_brand_url.name + '-' + str(get_brand_url.id)
                realpost['brand'] = brandurl

        tag_list = []
        tag_values = json.loads(post.get('tag_val'))
        if(len(tag_values) != 0):
            for i in tag_values:
                get_tags = request.env['product.tags'].search([('id','=',i)])
                tags_url = str(get_tags.name) + '-' + str(i)
                tag_list.append(tags_url)
            domain += [('product_tags_ids', 'in',tag_values)]

        if rating != None:
            domain = expression.AND([[('product_rating','>=',rating)], domain])

        Product = request.env['product.template']
        search_product = Product.search(domain,order=super()._get_search_order(post))
        url = '/shop'
        if search:
            post['search'] = search
            realpost['search'] = search
        if attrib_list:
            post['attrib'] = attrib_list
        if len(tag_list) != 0:
            realpost['tags'] = tag_list
        if category:
            url = '/shop/category/%s' % slug(category)
        if post.get('order'):
            realpost['order'] = post.get('order')
        if post.get('rating'):
            realpost['rating'] = post.get('rating')

        product_count = len(search_product)
        ppg = int(ppg)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=realpost)

        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        keep = QueryURL('/shop', category=category and int(category), search=None,tags=tag_list,attrib=attrib_list,
                        order=post.get('order'),brand=post.get('brand'),
                        min_val=post.get('min_val'),max_val=post.get('max_val'),
                        rating=post.get('rating'))
        bins = TableCompute().process(products, ppg, ppr)
        temp_of_prod = request.env.ref('atharva_theme_base.ajax_product')._render({'bins':bins,
                        'pager': pager,'keep':keep,'website_sale_order': order})
        pager_template = request.env['ir.ui.view']._render_template('portal.pager', {'pager':pager})
        data = {'product':temp_of_prod,'max_page':pager['page_count'],
                'pagerheader': page,'pager_template':pager_template}
        return data

    @http.route('/shop/brands', type='http', auth='public', website=True, sitemap=False)
    def all_brands(self, **post):
        values = {}
        domain = [('active','=',True),('visible_slider','=',True)] + request.website.website_domain()
        if post.get('search'):
            domain += [('name', 'ilike', post.get('search'))]
        brand_ids = request.env['as.product.brand'].search(domain)
        keep = QueryURL('/shop/brands', brand_id=[])
        if brand_ids:
            values.update({'brands': brand_ids,'keep': keep})
        if post.get('search'):
            values.update({'search': post.get('search')})
        return request.render('atharva_theme_base.product_brands', values)

    @http.route(['/shop/brand/<model("as.product.brand"):brand>'], type='http', auth='public', website=True, sitemap=False)
    def product_brand(self, brand=None, **post):
        domain = [('id', '=', int(brand)), ('active', '=', True)] + request.website.website_domain()
        if brand:
            brand = request.env['as.product.brand'].search(domain, limit=1)
            if not brand:
                raise NotFound()
            data = {'brand': brand,'products': brand.brand_product_ids}
            return request.render('atharva_theme_base.as_product_brands', data)
        return False

    @http.route()
    def cart(self, access_token=None, revive='', **post):
        res = super(WebsiteSale, self).cart(access_token=access_token, revive=revive, **post)
        if post.get('type') == 'cart_lines_popup':
            return request.render('atharva_theme_base.cart_lines_popup_content', res.qcontext)
        else:
            return res

    @http.route('/json/alternative_product/' ,type='json',auth='public',website=True)
    def json_alternative_product(self,**kwargs):
        getproduct = request.env['product.template'].search([('id','=',kwargs['prod_tmp_id'])])
        getSimilarProd = getproduct.alternative_product_ids
        get_temp_id = request.website.sudo().theme_id.name + ".quick_alter_prod_template"
        get_template = request.env['ir.ui.view']._render_template(get_temp_id, {'products':getSimilarProd})
        return {'quickAlterTemp':get_template}

    def _prepare_product_values(self, product, category, search, **kwargs):
        res = super(WebsiteSale, self)._prepare_product_values(product, category, search, **kwargs)
        ProductCategory = request.env['product.public.category']
        if(category):
            category = ProductCategory.browse(int(category)).exists()
            if len(category.parent_id) != 0:
                    res.update({'isSubcatetgory':category})
        return res

class JsonAuthSystem(Home):

    @http.route('/json/web/login', type='json', auth="none")
    def json_web_login(self, **kwargs):
        request.params['login_success'] = False
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        values = request.params.copy()
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.params
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')
        return values

    @http.route('/json/login/',type='json',auth="public")
    def json_login_templete(self,**kwargs):
        context = {}
        providers = OAuthLogin.list_providers(self)
        context.update(super().get_auth_signup_config())
        context.update({'providers':providers})
        signup_enabled = request.env['res.users']._get_signup_invitation_scope() == 'b2c'
        reset_password_enabled = request.env['ir.config_parameter'].sudo().get_param('auth_signup.reset_password') == 'True'
        get_temp_id = kwargs['theme_name'] + ".json_login_template"
        login_template = request.env['ir.ui.view']._render_template(get_temp_id,context)
        data = {'loginTemp':login_template}
        if(signup_enabled == True):
            get_temp_id = kwargs['theme_name'] + ".json_register_template"
            signup_template = request.env['ir.ui.view']._render_template(get_temp_id,context)
            data.update({'signupTemp':signup_template})
        if(reset_password_enabled == True):
            get_temp_id = kwargs['theme_name'] + ".json_reset_template"
            reset_template = request.env['ir.ui.view']._render_template(get_temp_id,context)
            data.update({'resetTemp':reset_template})
        return data

    @http.route('/json/signup/',type="json",auth="public")
    def json_web_auth_signup(self,*args, **kw):
        qcontext = super(JsonAuthSystem,self).get_auth_signup_qcontext()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                super(JsonAuthSystem,self).do_signup(qcontext)
                return {'signup_success':True}
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))]):
                    qcontext['error'] = _('Another user is already registered using this email address.')
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _('Could not create a new account.')
        return qcontext

    @http.route('/json/web/reset_password', type='json', auth='public', website=True, sitemap=False)
    def json_web_auth_reset_password(self, *args, **kw):
        qcontext = super(JsonAuthSystem,self).get_auth_signup_qcontext()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                login = qcontext.get('login')
                assert login, _('No login provided.')
                _logger.info(
                    'Password reset attempt for <%s> by user <%s> from %s',
                    login, request.env.user.login, request.httprequest.remote_addr)
                request.env['res.users'].sudo().reset_password(login)
                qcontext['message'] = _('An email has been sent with credentials to reset your password')
            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _('Could not reset your password')
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)
        return qcontext

class PwaFileConfig(http.Controller):
    def get_pwa_data(self,web_id):
        pwa = request.env['website'].search([('id','=',web_id)])
        big_img = request.website.image_url(pwa,'pwa_big_image')
        small_img = request.website.image_url(pwa,'pwa_small_image')
        return {
                'short_name': pwa.pwa_short_name,
                'name':  pwa.pwa_name,
                'description':pwa.pwa_description,
                'icons': [
                     {
                        'src': small_img,
                        'type': 'image/png',
                        'sizes': '192x192',
                        'purpose': 'any maskable'
                    },
                    {
                        'src': big_img,
                        'type': 'image/png',
                        'sizes': '512x512',
                        'purpose': 'any maskable'
                    }
                ],
                'start_url': '/',
                'background_color': pwa.pwa_bg_color,
                'display': 'standalone',
                'theme_color':pwa.pwa_theme_color,
        }

    @http.route('/manifest/webmanifest', type='http', auth='public',website=True, sitemap=False)
    def pwa_manifest_data(self,**kwargs):
        web_id = kwargs.get('web_id')
        return request.make_response(json.dumps(self.get_pwa_data(web_id)),
            headers=[('Content-Type', 'application/json;charset=utf-8')])

    @http.route('/service-worker-js', type='http', auth='public')
    def service_worker_rendering(self):
        return request.render('atharva_theme_base.service_worker',
            headers=[('Content-Type', 'text/javascript;charset=utf-8')])

    @http.route('/offline/page',type='http',auth='public')
    def offline_pwa(self):
        return request.render('atharva_theme_base.offline_pwa')

    @http.route('/pwa/is_active',type='json',auth='public',website=True)
    def pwa_is_active(self):
        return request.website.is_pwa_active