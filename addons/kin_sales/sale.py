# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html

from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from urllib import urlencode
from urlparse import urljoin
import  time


class CrmTeamExtend(models.Model):
    _inherit = 'crm.team'

    warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse')
    sale_stock_location_ids = fields.Many2many('stock.location',string="Sale Stock Locations",help="stock locations where sold items are to delivered from")

    @api.model
    def _get_default_team_id(self, user_id=None):
        res = None
        # settings_obj = self.env['sale.config.settings']
        # is_select_sales_team  = settings_obj.search([('is_select_sales_team', '=', True)], limit=1)
        is_select_sales_team  = self.env.user.company_id.is_select_sales_team
        if not is_select_sales_team :
            res = super(CrmTeamExtend,self)._get_default_team_id(user_id=user_id)
        return  res

class ResCompanyExtend(models.Model):
    _inherit = "res.company"

    is_select_sales_team = fields.Boolean(string='Users Must Select Sales Channel. otherwise pre-select the default Sales channel', help="By default, the system select the default sales team, but if the box is checked, then it clear the selection, for users to select themselves manually")
    is_contraint_sales_order_stock =  fields.Boolean('Do not allow confirmation of sales if stock is lesser than ordered quantity during Sales order confirmation')
    is_sales_order_stock_notification =  fields.Boolean('Send Email Notification if stock is lesser than ordered quantity during Sales order confirmation')
    is_sales_order_stock_purchase_request =  fields.Boolean('Send Email Notification with new created purchase Request if stock is lesser than ordered quantity during Sales order confirmation')
    is_send_stock_notification = fields.Boolean('Send Daily Stock Minimum Notification Report')
    is_invoice_before_delivery = fields.Boolean('Create Invoice from Sales Ordered Qty. before Delivery',help='This should be used for products with fixed/standard costing method')
    is_send_invoice_notification = fields.Boolean('Send Invoice Email Notification on Sales ordered quantity',help='This should be used for products with fixed/standard costing method')
    is_po_check = fields.Boolean('Forces Sales Person to Enter a PO Reference', default=True)



class SaleOrderExtend(models.Model):
    _inherit = "sale.order"

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        res = super(SaleOrderExtend, self).copy(default)
        res.so_name = False
        return res

    @api.model
    def create(self, vals):
        order = super(SaleOrderExtend, self).create(vals)
        order.quote_name = order.name
        return order

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = amt_discount_total = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amt_discount_total += line.discount_amt
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                'amt_discount_total' : order.pricelist_id.currency_id.round(amt_discount_total)
            })

    @api.multi
    def action_cancel(self):
        self.show_alert_box = False
        self.show_alert_box1 = False
        for picking in self.picking_ids:
            if picking.state == "done":
                raise UserError(_("Sorry, a delivery has been completed, this sales order cannot be cancelled"))

        return  super(SaleOrderExtend,self).action_cancel()


    @api.onchange('team_id')
    def _team_id(self):
        if self.team_id.warehouse_id:
            self.warehouse_id = self.team_id.warehouse_id.id
        else :
            company = self.env.user.company_id.id
            self.warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)


    @api.multi
    def action_view_delivery(self):
        res = super(SaleOrderExtend,self).action_view_delivery()
        res['target'] = 'new'
        return  res


    def _get_invoice_url(self, module_name,menu_id,action_id, context=None):
        fragment = {}
        res = {}
        model_data = self.env['ir.model.data']
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        fragment['menu_id'] = model_data.get_object_reference(module_name,menu_id)[1]
        fragment['model'] =  'account.invoice'
        fragment['view_type'] = 'form'
        fragment['action']= model_data.get_object_reference(module_name,action_id)[1]
        query = {'db': self.env.cr.dbname}

# for displaying tree view. Remove if you want to display form view
#         fragment['page'] = '0'
#         fragment['limit'] = '80'
#         res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


 # For displaying a single record. Remove if you want to display tree view

        fragment['id'] =  context.get("invoice_id")
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res



    def _get_url(self, module_name,menu_id,action_id, context=None):
        fragment = {}
        res = {}
        model_data = self.env['ir.model.data']
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        fragment['menu_id'] = model_data.get_object_reference(module_name,menu_id)[1]
        fragment['model'] =  'stock.picking'
        fragment['view_type'] = 'form'
        fragment['action']= model_data.get_object_reference(module_name,action_id)[1]
        query = {'db': self.env.cr.dbname}
# for displaying tree view. Remove if you want to display form view
#         fragment['page'] = '0'
#         fragment['limit'] = '80'
#         res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


 # For displaying a single record. Remove if you want to display tree view
        fragment['id'] =  context.get("picking_id")
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res

    @api.multi
    def close_alert_box(self):
        self.show_alert_box = False
        return

    @api.multi
    def close_alert_box1(self):
        self.show_alert_box1 = False
        return


    def check_line_qty(self,sale_stock_loc_ids):
        listdata= []
        product_obj = self.env['product.product']
        ctx = self.env.context.copy()

        for sale_order in self :
            for sale_order_line in sale_order.order_line :
                product  = sale_order_line.product_id
                product_id = product.id
                product_name = product.name
                min_alert_qty = product.min_alert_qty
                order_line_qty = sale_order_line.product_uom_qty
                qty_available = 0
                if sale_order_line.product_id.type == 'product':
                    for location_id in sale_stock_loc_ids :
                        ctx.update({"location":location_id.id})
                        res = product_obj.browse([product_id])[0].with_context(ctx)._product_available()
                        qty_available += res[product_id]['qty_available']

                    product_qty = self.env['product.uom']._compute_qty_obj(sale_order_line.product_uom, order_line_qty, sale_order_line.product_id.uom_id)
                    if qty_available < product_qty    :
                        listdata.append({product_name:qty_available})
        return listdata

    def _get_purchase_request_url(self, module_name,menu_id,action_id, context=None):
        fragment = {}
        res = {}
        model_data = self.env['ir.model.data']
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        fragment['menu_id'] = model_data.get_object_reference(module_name,menu_id)[1]
        fragment['model'] =  'purchase.request'
        fragment['view_type'] = 'form'
        fragment['action']= model_data.get_object_reference(module_name,action_id)[1]
        query = {'db': self.env.cr.dbname}

# for displaying tree view. Remove if you want to display form view
#         fragment['page'] = '0'
#         fragment['limit'] = '80'
#         res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


 # For displaying a single record. Remove if you want to display tree view

        fragment['id'] =  context.get("request_id")
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


        return res


    def create_purchase_request(self,sale_stock_loc_ids):
        purchase_request_obj = self.env['purchase.request']
        sale_order_line_obj = self.env['sale.order.line']
        lines =[]
        for sale_order in self :
            for sale_line in sale_order.order_line :
                low_stock_dict = sale_line.check_order_line_qty_location(sale_stock_loc_ids)
                if low_stock_dict :
                    product_id = low_stock_dict.keys()[0]
                    lines += [(0,0, {
                        'product_id':product_id,
                        'product_qty': sale_line.product_uom_qty,
                        'name' : sale_line.name,
                    })
                    ]
        vals = {
                'origin' : self.name,
                'description': self.user_id.name + " was about selling the following listed items with zero stock level. Please request for the items to be purchased from the manager. The sales order reference is: " + self.name ,
                'line_ids':lines
            }
        pr_id = purchase_request_obj.create(vals)
        return pr_id


    @api.multi
    def action_cancel(self):
        #delete draft invoices, else invoice wil raise error
        self.invoice_ids.unlink()
        unqualified_picks = 0
        for picking in self.picking_ids:
            if picking.state <> 'draft' and picking.state != 'confirmed':
                unqualified_picks += 1
        if unqualified_picks == 0:
            self.picking_ids.unlink()

        res = super(SaleOrderExtend,self).action_cancel()
        return res


    @api.multi
    def action_confirm(self):
        list_data = []
        is_contraint_sales_order_stock  = self.env.user.company_id.is_contraint_sales_order_stock
        is_sales_order_stock_notification  = self.env.user.company_id.is_sales_order_stock_notification
        is_sales_order_stock_purchase_request  = self.env.user.company_id.is_sales_order_stock_purchase_request
        is_po_check = self.env.user.company_id.is_po_check

        customer = self.partner_id

        #is PO Check
        if is_po_check :
            if self.client_order_ref :
                client_order_ref = self.client_order_ref.strip()

                if len(client_order_ref) <= 0 :
                    raise UserError('Please Ensure that the Quote is confirmed from the customer and that the PO reference is set. e.g. you may put the po number, email, contact name, number of the customer that confirmed the Quote on the PO reference field')

            else :
                raise UserError('Please Ensure that the Quote is confirmed from the customer and that the PO reference is set. e.g. you may put the po number, email, contact name, number of the customer that confirmed the Quote')

        #Credit limit Check
        if customer.is_enforce_credit_limit_so :
            if self.amount_total > customer.allowed_credit :
                raise UserError('Total Amount %s%s has exceeded the remaining credit %s%s for %s' % (self.currency_id.symbol,self.amount_total,self.currency_id.symbol,customer.allowed_credit,customer.name))


        if  is_contraint_sales_order_stock or is_sales_order_stock_notification or is_sales_order_stock_purchase_request :
            # Check product qty if is less than 0 for each location
            for sale_order in self :
                stock_locations = ""
                sale_team = sale_order.team_id
                sale_stock_loc_ids = sale_team.sale_stock_location_ids
                list_data  = self.check_line_qty(sale_stock_loc_ids)

                if len(list_data) > 0 :
                    for stock_location in sale_stock_loc_ids:
                        stock_locations += stock_location.name + ", "
                    stock_locations= stock_locations.rstrip(', ')
                    msg = ""
                    sale_msg = ""
                    sale_msg += "The following Items are lesser than the quantity available in the stock locations (%s) \n" % (stock_locations)
                    count = 0
                    for data_dict in list_data:
                        for key, value in data_dict.iteritems(): # keys = data_dict.keys()  # see ref: http://stackoverflow.com/questions/5904969/python-how-to-print-a-dictionarys-key
                            msg += "%s (%s) qty. is lesser than the quantity available in the stock locations (%s) \n" %  (key,value,stock_locations)
                            count+=1
                            sale_msg = "%s). %s (%s) qty. \n" %  (count,key,value)
                    msg += "Please contact the purchase manager to create purchase order for the item(s) \n"

                    company_email = self.env.user.company_id.email.strip()

                    #Create and Send Purchase Request Notification
                    if company_email and is_sales_order_stock_purchase_request :

                        pr_id = self.create_purchase_request(sale_stock_loc_ids)
                        ctx = {}
                        ctx.update({'request_id':pr_id.id})
                        the_url = self._get_purchase_request_url('purchase_request','menu_purchase_request_pro_mgt','purchase_request_form_action',ctx)
                        mail_template = self.env.ref('kin_sales.mail_templ_purchase_request_email_sales_stock')
                        users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

                        for user in users :
                            if user.has_group('kin_sales.group_receive_sale_order_purchase_request_email') and user.partner_id.email and user.partner_id.email.strip() :
                                ctx = {'system_email': company_email,
                                        'purchase_request_email':user.partner_id.email,
                                        'partner_name': user.partner_id.name ,
                                        'sale_order_name': sale_order.name,
                                        'url' : the_url,
                                    }
                                mail_template.with_context(ctx).send_mail(pr_id.id,force_send=False) #Before force_send was True
                                self.show_alert_box1 = True

                    #Send Email to purchase person
                    if is_contraint_sales_order_stock and not is_sales_order_stock_notification :
                        raise UserError(_(msg))
                    elif company_email and is_contraint_sales_order_stock and is_sales_order_stock_notification:
                        # Custom Email Template
                        mail_template = self.env.ref('kin_sales.mail_templ_purchase_stock_level_email_sales_stock_alert')
                        users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

                        users_msg = ""
                        for user in users :
                            if user.has_group('kin_sales.group_receive_sale_order_stock_alert_email') and user.partner_id.email and user.partner_id.email.strip() :
                                ctx = {'system_email': company_email,
                                        'purchase_stock_email':user.partner_id.email,
                                        'partner_name': user.partner_id.name ,
                                        'sale_order_name': sale_order.name,
                                        'stock_locations' : stock_locations,
                                        'msg' : sale_msg
                                        }
                                mail_template.with_context(ctx).send_mail(sale_order.id,force_send=True) # It has to force send the email, before hitting the user error below, otherwise it will not send the email because of the user error raised below
                                self.show_alert_box1 = True
                                users_msg += user.partner_id.name + ", "
                        users_msg = users_msg.rstrip(", ")
                        if users_msg :
                            msg += "However, A Stock Alert Email for the item(s) has been sent to %s ." % (users_msg)
                        raise UserError(_(msg))

                    elif company_email and not is_contraint_sales_order_stock and is_sales_order_stock_notification :
                        # Custom Email Template
                        mail_template = self.env.ref('kin_sales.mail_templ_purchase_stock_level_email_sales_stock_alert')
                        users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

                        users_msg = ""
                        for user in users :
                            if user.has_group('kin_sales.group_receive_sale_order_stock_alert_email') and user.partner_id.email and user.partner_id.email.strip() :
                                ctx = {'system_email': company_email,
                                        'purchase_stock_email':user.partner_id.email,
                                        'partner_name': user.partner_id.name ,
                                        'sale_order_name': sale_order.name,
                                        'stock_locations' : stock_locations,
                                        'msg' : sale_msg
                                    }
                                mail_template.with_context(ctx).send_mail(sale_order.id,force_send=False)
                                self.show_alert_box1 = True

        if self.so_name:
            self.name = self.so_name
        else:
            self.quote_name = self.name
            self.name = self.env['ir.sequence'].get('so_id_code')
            self.so_name = self.name
        res = super(SaleOrderExtend, self).action_confirm()

        picking_id = self.picking_ids and  self.picking_ids[0]

        # Send Email to the Stock Person
        company_email = self.env.user.company_id.email.strip()
        if company_email and picking_id :
            # Custom Email Template
            mail_template = self.env.ref('kin_sales.mail_templ_delivery_transfer_created')
            ctx = {}
            ctx.update({'picking_id':picking_id.id})
            the_url = self._get_url('stock','all_picking','action_picking_tree_all',ctx)
            users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

            for user in users :
                if user.has_group('kin_sales.group_receive_delivery_stock_transfer_email') and user.partner_id.email and user.partner_id.email.strip() :
                    ctx = {'system_email': company_email,
                            'stock_person_email':user.partner_id.email,
                            'stock_person_name': user.partner_id.name ,
                            'url':the_url,
                            'origin': picking_id.origin
                        }
                    mail_template.with_context(ctx).send_mail(picking_id.id,force_send=False)
                    self.show_alert_box = True


        # Create Invoice on Ordered Quantity. This should be used for Stock configured with Standard Cost
        is_invoice_before_delivery = self.env.user.company_id.is_invoice_before_delivery
        is_send_invoice_notification = self.env.user.company_id.is_send_invoice_notification


        if is_invoice_before_delivery :
            inv = self.create_customer_invoice()
            # Send Email to the Accountant
            company_email = self.env.user.company_id.email.strip()
            if company_email and  is_send_invoice_notification:
                # Custom Email Template
                mail_template = self.env.ref('kin_sales.mail_templ_invoice_before_delivery')
                ctx = {}
                ctx.update({'invoice_id':inv.id})
                the_invoice_url = self._get_invoice_url('account','menu_action_invoice_tree2','action_invoice_tree2',ctx)
                users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

                for user in users :
                    if user.has_group('kin_sales.group_invoice_before_delivery_email') and user.partner_id.email and user.partner_id.email.strip() :
                        ctx = {'system_email': company_email,
                                'accountant_email':user.partner_id.email,
                                'accountant_name': user.partner_id.name ,
                                'url':the_invoice_url,
                                'origin' : self.name,
                                'partner_name' : self.partner_id.name
                            }
                        mail_template.with_context(ctx).send_mail(inv.id,force_send=False)

        return res

    @api.multi
    def action_draft(self):
        res = super(SaleOrderExtend, self).action_draft()
        if self.quote_name:
            self.name = self.quote_name
        return res



    show_alert_box  = fields.Boolean(string="Show Alert Box")
    amt_discount_total = fields.Monetary(string='Discounts', store=True, readonly=True, compute='_amount_all')
    show_alert_box1  = fields.Boolean(string="Show Alert Box1")
    sale_shipping_term_id = fields.Many2one('sale.shipping.term', string='Shipping Term')
    date_order = fields.Datetime(string='Order Date',  required=True, readonly=True, index=True,states={'draft': [('readonly', False),('required',False)], 'sent': [('readonly', False)], 'waiting': [('readonly',False)]}, copy=False)
    date_quote = fields.Datetime(string='Quote Date',  required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    so_name = fields.Char('SO Name')
    quote_name = fields.Char('Quote Name')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sale Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.multi
    def action_view_invoice(self):
        res = super(SaleOrderExtend,self).action_view_invoice()
        res['target'] = 'new'
        return  res

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderExtend,self)._prepare_invoice()
        if self.env.user.company_id.inv_note and len(self.env.user.company_id.inv_note.strip()) > 0 :
            invoice_vals['comment'] = self.env.user.company_id.inv_note
        return  invoice_vals



    def create_customer_invoice(self):

        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}

        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))

        invoice_vals = {
            'name':  '',
            'origin': self.name,
            'type': 'out_invoice',
            'reference': self.client_order_ref or '',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'incoterms_id' : self.incoterm.id or False
        }

        invoice = inv_obj.create(invoice_vals)

        lines = []
        for sale_order_line_id in self.order_line:

            if not float_is_zero(sale_order_line_id.product_uom_qty, precision_digits=precision):
                account = sale_order_line_id.product_id.property_account_income_id or sale_order_line_id.product_id.categ_id.property_account_income_categ_id
                if not account:
                    raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') % (sale_order_line_id.product_id.name, sale_order_line_id.product_id.id, sale_order_line_id.product_id.categ_id.name))

                fpos = sale_order_line_id.order_id.fiscal_position_id or sale_order_line_id.order_id.partner_id.property_account_position_id
                if fpos:
                    account = fpos.map_account(account)

                default_analytic_account = self.env['account.analytic.default'].account_get(sale_order_line_id.product_id.id, sale_order_line_id.order_id.partner_id.id, sale_order_line_id.order_id.user_id.id, time.strftime('%Y-%m-%d'))

                inv_line = {
                        'name': sale_order_line_id.name,
                        'sequence': sale_order_line_id.sequence,
                        'origin': sale_order_line_id.order_id.name,
                        'account_id': account.id,
                        'price_unit': sale_order_line_id.price_unit,
                        'quantity':  sale_order_line_id.product_uom_qty,
                        'discount': sale_order_line_id.discount,
                        'uom_id': sale_order_line_id.product_uom.id,
                        'product_id': sale_order_line_id.product_id.id or False,
                       'invoice_line_tax_ids': [(6, 0, sale_order_line_id.tax_id.ids)],
                       'account_analytic_id':  sale_order_line_id.order_id.project_id.id  or default_analytic_account and default_analytic_account.analytic_id.id,
                       'invoice_id': invoice.id ,
                       'sale_line_ids': [(6, 0, [sale_order_line_id.id])]
                }
                self.env['account.invoice.line'].create(inv_line)


        if not invoice.invoice_line_ids:
            raise UserError(_('There is no invoiceable line.'))
            # If invoice is negative, do a refund invoice instead
        if invoice.amount_untaxed < 0:
            invoice.type = 'out_refund'
            for line in invoice.invoice_line_ids:
                line.quantity = -line.quantity
        # Use additional field helper function (for account extensions)
        for line in invoice.invoice_line_ids:
            line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
        invoice.compute_taxes()

        return invoice


class SalesShippingTerms(models.Model):
    _name = 'sale.shipping.term'

    name = fields.Char(string='Shipping Term')
    description = fields.Text(string='Description')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # @api.multi
    # def _prepare_order_line_procurement(self, group_id=False):
    #     res = super(SaleOrderLine,self)._prepare_order_line_procurement(group_id)
    #     res['po_ref'] = self.order_id.client_order_ref
    #     return res



    @api.model
    def create(self, vals):
        product_id = vals.get('product_id', False)
        if product_id:
            product_obj = self.env['product.product'].browse(product_id)
            description_sale = product_obj.description_sale
            if description_sale and len(description_sale.strip()) > 0:
                vals['name'] = description_sale
            else:
                vals['name'] = product_obj.name
        return super(SaleOrderLine, self).create(vals)

    @api.onchange('discount_amt')
    def _onchange_discount_amt(self):
        for line in self:
            if line.price_unit:
                disc_amt = line.discount_amt
                taxes = line.tax_id.compute_all((line.price_unit-disc_amt), line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)

                #means to write to the database fields. you can do direct assignment, but it is not suitable,
                # because, it will hit the database for the number of writes/assignment. e.g. line.price_subtotal = taxes['total_excluded']
                line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'discount' : (disc_amt / line.price_unit) * 100
            })

    @api.onchange('discount')
    def _onchange_discount(self):
        for line in self:
            if line.price_unit:
                disc_amt =  (line.discount / 100) * line.price_unit
                line.discount_amt = disc_amt


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        res = super(SaleOrderLine,self)._compute_amount()
        self._onchange_discount()

    def check_order_line_qty_location(self,sale_stock_loc_ids):
        ctx = self.env.context.copy()
        product_obj = self.env['product.product']
        for sale_order_line in self :
            product  = sale_order_line.product_id
            product_id = product.id
            order_line_qty = sale_order_line.product_uom_qty
            qty_available = 0
            if sale_order_line.product_id.type == 'product':
                for location_id in sale_stock_loc_ids :
                    ctx.update({"location":location_id.id})
                    res = product_obj.browse([product_id])[0].with_context(ctx)._product_available()
                    qty_available += res[product_id]['qty_available']

                    order_line_product_qty = self.env['product.uom']._compute_qty_obj(sale_order_line.product_uom, order_line_qty, sale_order_line.product_id.uom_id)
                    if qty_available < order_line_product_qty    :
                        return {product_id:(qty_available,order_line_product_qty)}
        return {}

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.env['product.uom']._compute_qty_obj(self.product_uom, self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.virtual_available, product_qty, precision_digits=precision) == -1:

                sale_stock_loc_ids = self.order_id.team_id.sale_stock_location_ids
                res = self.check_order_line_qty_location(sale_stock_loc_ids)
                if res:
                    qty_available = res[self.product_id.id][0]
                    order_line_qty = res[self.product_id.id][1]
                    stck_list = ""
                    for stock_location in sale_stock_loc_ids :
                        stck_list += stock_location.name + ", "
                    stck_list = stck_list.rstrip(', ')
                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message' : _('You plan to sell %.2f %s of %s, but you only have %.2f %s available in the assigned stock location(s) (%s) \n The total stock on hand in the stock location(s) (%s) for %s is %.2f %s.') % \
                            (order_line_qty, self.product_uom.name, self.product_id.name, qty_available, self.product_id.uom_id.name,  stck_list, stck_list, self.product_id.name, qty_available, self.product_id.uom_id.name)
                    }
                    return {'warning': warning_mess}
        return {}


    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine,self).product_id_change()
        vals = {}
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        if product.description_sale:
            name = product.description_sale
            vals['name'] = name
            self.update(vals)
        return res



    discount_amt = fields.Float(string='Disc./Unit (Amt.)', digits=dp.get_precision('Discount'), default=0.0)
    date_order = fields.Datetime(string='Order date',related='order_id.date_order',ondelete='cascade', index=True,store=True)



class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self,vals):
        is_customer = vals.get('customer',False)
        is_supplier = vals.get('supplier',False)
        if is_customer :
            vals['ref'] = self.env['ir.sequence'].get('cust_id_code')
        elif is_supplier :
            vals['ref'] = self.env['ir.sequence'].get('supp_id_code')

        return super(ResPartner,self).create(vals)

# Reference: odoo community aged partner code for getting due amount
    def _get_not_due_amount_receivable(self):
        for partner in self :
            cr = self.env.cr
            partner_id = partner.id
            move_state = 'posted'
            account_type = 'receivable'
            date_from = fields.Date.context_today(self)
            user_company = self.env.user.company_id.id
            future_past = 0
            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state = %s)
                        AND (account_account.internal_type = %s)
                        AND (COALESCE(l.date_maturity,l.date) > %s)\
                        AND (l.partner_id = %s)
                    AND (l.date <= %s)
                    AND l.company_id = %s'''
            cr.execute(query, (move_state,account_type, date_from, partner_id, date_from, user_company))
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                line_amount = line.balance
                if line.balance == 0:
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.create_date[:10] <= date_from:
                        line_amount += partial_line.amount
                for partial_line in line.matched_credit_ids:
                    if partial_line.create_date[:10] <= date_from:
                        line_amount -= partial_line.amount
                future_past += line_amount
            partner.not_due_amount_receivable = future_past

    def _get_due_amount_receivable(self):
        for partner in self:
            partner.due_amount_receivable = partner.credit - partner.not_due_amount_receivable


    def _get_allowed_credit(self):
        for partner in self:
            allowed_credit = partner.credit_limit - partner.due_amount_receivable
            if allowed_credit < 0 :
                partner.allowed_credit = 0
            else :
                partner.allowed_credit = allowed_credit


    credit_limit = fields.Float(string='Credit Limit')
    is_enforce_credit_limit_so = fields.Boolean(string='Enforce Credit Limit on Sales Order')
    due_amount_receivable = fields.Float(string='Due',compute=_get_due_amount_receivable,help='Receivables that are Due to be paid')
    not_due_amount_receivable = fields.Float(string='Not Due',compute=_get_not_due_amount_receivable,help='Receivables that are Not Due to be Paid')
    allowed_credit = fields.Float(string='Remaining Credit Allowed',compute=_get_allowed_credit,help='Credit Allowance for the partner')

    # NOT NECESSARY, THE SYSTEM WORKS AS EXPECTED OUT OF THE BOX
    # @api.multi
    # def name_get(self): # Works when you are displaying the field name. e.g. when  tree view is loaded or form view is loaded
    #     result = []
    #     for partner in self:
    #         strf = "%s - %s" % (partner.name, partner.ref or '')
    #         item = (partner.id, strf)
    #         result.append(item)
    #     return result
    #
    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100): # Works when you are searching for a field name on a many2one field or the search bar
    #     args = args or []
    #     recs = self.browse()  # Initializes the variable, you can use recs = []
    #     if name:
    #         recs = self.search(['|', ('name', '=', name),('ref','=',name)] + args, limit=limit)
    #     if not recs:
    #         recs = self.search(['|', ('name', operator, name),('ref',operator,name)] + args, limit=limit)
    #     return recs.name_get()



