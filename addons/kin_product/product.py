# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html


from datetime import datetime, timedelta
from openerp import api, fields, models, _
from urllib import urlencode
from urlparse import urljoin


class ProductPricelistExtend(models.Model):
    _inherit = 'product.pricelist'

    operating_unit_id = fields.Many2one('operating.unit',string='Operating Unit')


class ProductTemplateExtend(models.Model):
    _inherit = 'product.template'



    def _get_url(self, module_name, menu_id, action_id, context=None):
        fragment = {}
        res = {}
        model_data = self.env['ir.model.data']
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        fragment['menu_id'] = model_data.get_object_reference(module_name, menu_id)[1]
        fragment['model'] = 'product.template'
        fragment['view_type'] = 'form'
        fragment['action'] = model_data.get_object_reference(module_name, action_id)[1]
        query = {'db': self.env.cr.dbname}
        # for displaying tree view. Remove if you want to display form view
        #         fragment['page'] = '0'
        #         fragment['limit'] = '80'
        #         res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


        # For displaying a single record. Remove if you want to display tree view
        fragment['id'] = context.get("product_id")
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res

    @api.model
    def create(self,vals):
        res = super(ProductTemplateExtend,self).create(vals)
        #notify the group people
        # Send Email
        company_email = self.env.user.company_id.email.strip()
        product_person_email = self.env.user.partner_id.email.strip()
        product_person_name = self.env.user.name


        if company_email and product_person_email:
            # Custom Email Template
            mail_template = self.env.ref('kin_product.mail_templ_create_product_email')
            ctx = {}
            ctx.update({'product_id': res.id})
            the_url = self._get_url('product', 'menu_product_template_action', 'product_template_action_product', ctx)

            user_ids = []
            group_obj = self.env.ref('kin_product.group_receive_create_product_email')
            for user in group_obj.users:
                if user.partner_id.email and user.partner_id.email.strip():
                    user_ids.append(user.id)
                    ctx = {'system_email': company_email,
                           'product_person_name': product_person_name,
                           'product_person_email': product_person_email,
                           'notify_person_email': user.partner_id.email,
                           'notify_person_name': user.partner_id.name,
                           'url': the_url,
                           'obj' : res,
                           }
                    mail_template.sudo().with_context(ctx).send_mail(self.id, force_send=False)
        return res

    # It repeats sending of email for the each edit for the fields. So no need
    # @api.multi
    # def write(self, vals):
    #     res = super(ProductTemplateExtend, self).write(vals)
    #     # notify the group people
    #     # Send Email
    #     company_email = self.env.user.company_id.email.strip()
    #     product_person_email = self.env.user.partner_id.email.strip()
    #     product_person_name = self.env.user.name
    #
    #     if company_email and product_person_email:
    #         # Custom Email Template
    #         mail_template = self.env.ref('kin_product.mail_templ_edit_product_email')
    #         ctx = {}
    #         ctx.update({'product_id': self.id})
    #         the_url = self._get_url('product', 'menu_product_template_action', 'product_template_action_product', ctx)
    #
    #         user_ids = []
    #         group_obj = self.env.ref('kin_product.group_receive_edit_product_email')
    #         for user in group_obj.users:
    #             if user.partner_id.email and user.partner_id.email.strip():
    #                 user_ids.append(user.id)
    #                 ctx = {'system_email': company_email,
    #                        'product_person_name': product_person_name,
    #                        'product_person_email': product_person_email,
    #                        'notify_person_email': user.partner_id.email,
    #                        'notify_person_name': user.partner_id.name,
    #                        'url': the_url
    #                        }
    #                 mail_template.with_context(ctx).send_mail(self.id, force_send=True)
    #     return res

    @api.multi
    def unlink(self):
        # notify the group people
        # Send Email
        company_email = self.env.user.company_id.email.strip()
        product_person_email = self.env.user.partner_id.email.strip()
        product_person_name = self.env.user.name

        if company_email and product_person_email:
            # Custom Email Template
            mail_template = self.env.ref('kin_product.mail_templ_delete_product_email')
            ctx = {}
            # ctx.update({'product_id': self.id})
            # the_url = self._get_url('product', 'menu_product_template_action', 'product_template_action_product', ctx)

            user_ids = []
            group_obj = self.env.ref('kin_product.group_receive_delete_product_email')
            for user in group_obj.users:
                if user.partner_id.email and user.partner_id.email.strip():
                    user_ids.append(user.id)
                    ctx = {'system_email': company_email,
                           'product_person_name': product_person_name,
                           'product_person_email': product_person_email,
                           'notify_person_email': user.partner_id.email,
                           'notify_person_name': user.partner_id.name,
                           # 'url': the_url
                           }
                    mail_template.with_context(ctx).send_mail(self.id, force_send=True) #You have to force send at this point, because the specific record will be deleted soon
        return super(ProductTemplateExtend, self).unlink()


    @api.model
    def run_min_alert_qty_check(self):

        # settings_obj = self.env['sale.config.settings']
        # is_send_stock_notification  = settings_obj.search([('is_send_stock_notification', '=', True)], limit=1)
        is_send_stock_notification  = self.env.user.company_id.is_send_stock_notification
        if  is_send_stock_notification :
            product_obj = self.env['product.product']
            stock_location_obj = self.env['stock.location']
            ctx = self.env.context.copy()

            the_date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
            msg = "<style> " \
                    "table, th, td {" \
                    "border: 1px solid black; " \
                    "border-collapse: collapse;" \
                    "}" \
                    "th, td {" \
                    "padding-left: 5px;"\
                    "}" \
                    "</style>"
            msg += "<p>Hello,</p>"
            msg += "<p>Please see the Minimum Stock Notification as of %s</p><p></p>"  % (the_date)
            msg += "<table width='100%' >"

            at_least_one = False
            stock_locations = stock_location_obj.search([('usage','=','internal')])
            products = product_obj.search([])

            for stock_location in stock_locations :
                count = 0
                msg +=  "<tr><td colspan='5' align='center' style='margin:35px' ><h2>"+ stock_location.name +"</h2></td></tr>" \
                 "<tr align='left' ><th>S/N</th><th>Product Name</th><th>Unit</th><th>Min. Alert Qty</th><th>Qty. Available</th></tr>"

                ctx.update({'location':stock_location.id})
                for product in products :
                    min_alert_qty = product.min_alert_qty
                    is_included_in_min_alert_qty = product.is_included_in_min_alert_qty
                    product_id = product.id
                    product_name = product.name
                    product_uom = product.uom_id.name
                    res = product_obj.browse([product_id]).with_context(ctx)._product_available()
                    qty_available = res[product_id]['qty_available']
                    if (qty_available <= min_alert_qty) and is_included_in_min_alert_qty:
                        count += 1
                        at_least_one = True
                        msg += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (count,product_name,product_uom,min_alert_qty,qty_available)

            msg += "</table> <p></p><p>You may manually create purchase order for the listed items, to replenish the stock</p>" \
				  "<p>Regards and Thanks</p>" \
				  "<p>This is an autogenerated message from %s ERP System</p>" % (self.env.user.company_id.name)


            #Send Email
            company_email = self.env.user.company_id.email.strip()
            if company_email and at_least_one :
                # Custom Email Template
                #mail_template = self.env.ref('kin_sales.mail_templ_min_alert_stock_level')
                users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

                for user in users :
                    if user.has_group('kin_sales.group_minimum_stock_notification_email') and user.partner_id.email and user.partner_id.email.strip() :
                        # ctx = {'system_email': company_email,
                        #         'user_email':user.partner_id.email,
                        #         'partner_name': user.partner_id.name ,
                        #         'msg' : msg,
                        #         'the_date' : the_date ,
                        #        }
                        #Not used because it renders the raw html table rather than evaluating the html
                        #mail_template.with_context(ctx).send_mail(self.id,force_send=False)

                        #Send Email
                        mail_obj = self.env['mail.mail']
                        mail_data = {
                            'model': 'product.template',
                            'res_id': self.id,
                            'record_name': 'Minimum Alert Stock Level',
                            'email_from': company_email,
                            'reply_to': company_email,
                            'subject': "Minimum Stock Level Notification for the date %s" % (the_date),
                            'body_html': '%s' % msg,
                            'auto_delete': True,
                            #'recipient_ids': [(4, id) for id in new_follower_ids]
                            'email_to': user.partner_id.email
                        }
                        mail_id = mail_obj.create(mail_data)
                        mail_obj.send([mail_id])


            return True


    name = fields.Char('Name', required=True, translate=True, select=True,track_visibility = "onchange")
    description_sale =  fields.Text('Sale Description', translate=True,
                                    help="A description of the Product that you want to communicate to your customers. "
                                         "This description will be copied to every Sale Order, Delivery Order and Customer Invoice/Refund",
                                    track_visibility="onchange"
                                    )

    description_purchase = fields.Text('Purchase Description', translate=True,
                                        help="A description of the Product that you want to communicate to your vendors. "
                                             "This description will be copied to every Purchase Order, Receipt and Vendor Bill/Refund.",
                                        track_visibility = "onchange")

    description_picking = fields.Text('Description on Picking', translate=True,track_visibility = "onchange")
    min_alert_qty = fields.Float(string='Minimum Alert Qty.', help="Minimum Alert Qty. for the Item to be Included in the Notification Report")
    is_included_in_min_alert_qty = fields.Boolean(string="Include M.A.Q. in Notif.", help="Include this product in the email message that is sent sent by the scheduler")
