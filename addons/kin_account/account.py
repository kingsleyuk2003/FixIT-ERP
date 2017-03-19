# -*- coding: utf-8 -*-


from openerp import api, fields, models, _



class AccountJournalExtend(models.Model):
    _inherit = "account.journal"


    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account', help='This helps to automatically populate the invoices with the set analytic account')




class AccountAnalyticLineExtend(models.Model):
    _inherit = 'account.analytic.line'

    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    invoice_line_id = fields.Many2one('account.invoice.line',string="Invoice Line")