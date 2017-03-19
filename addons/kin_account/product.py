# -*- coding: utf-8 -*-


from openerp import api, fields, models, _



class ProductTemplateExtend(models.Model):
    _inherit = 'product.template'

    disc_acct_analytic_purchase_id = fields.Many2one('account.analytic.account',string="Purchase Discount Analytic Account")
    disc_acct_analytic_sale_id = fields.Many2one('account.analytic.account',string="Sales Discount Analytic Account")
    # disc_acct_sale_id = fields.Many2one('account.account',string='Sales Discount Account',help="Records sales discount transactions for this product")
    # disc_acct_purchase_id = fields.Many2one('account.account',string='Purchase Discount Account',help="Records purchase discount transactions for this product")
    # purchase_acc_id = fields.Many2one('account.account',string='Purchase Income Account',help="Records expenses transactions for this product")
    # income_acc_id = fields.Many2one('account.account',string='Purchase Income Account',help="Records income transactions for this product")

class ProductCategoryExtend(models.Model):
    _inherit = "product.category"

    disc_acct_analytic_purchase_id = fields.Many2one('account.analytic.account',string="Purchase Discount Analytic Account")
    disc_acct_analytic_sale_id = fields.Many2one('account.analytic.account',string="Sales Discount Analytic Account")
    # disc_acct_purchase_id = fields.Many2one('account.account',string='Purchase Discount Account',help="Records purchase discount transactions for this product")
    # disc_acct_sale_id = fields.Many2one('account.account',string='Sales Discount Account',help="Records sales discount transactions for this product")
    # purchase_acc_id = fields.Many2one('account.account',string='Purchase Expense Account',help="Records expenses transactions for this product")
    # income_acc_id = fields.Many2one('account.account',string='Purchase Income Account',help="Records income transactions for this product")
