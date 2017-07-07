# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html

from openerp import api, fields, models, _

class AccountAccountExtend(models.Model):
    _inherit = 'account.account'

    tag_ids = fields.Many2many('account.account.tag', 'account_account_account_tag', 'account_account_id','account_account_tag_id')

class AccountAccountTagExtend(models.Model):
    _inherit = 'account.account.tag'

    account_ids = fields.Many2many('account.account','account_account_account_tag','account_account_tag_id' ,'account_account_id', string="Accounts")


class AccountJournalExtend(models.Model):
    _inherit = "account.journal"

    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account', help='This helps to automatically populate the invoices with the set analytic account')


class AccountAnalyticLineExtend(models.Model):
    _inherit = 'account.analytic.line'

    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    invoice_line_id = fields.Many2one('account.invoice.line',string="Invoice Line")


class AccountMoveExtend(models.Model):
    _name = 'account.move'
    _inherit = ['account.move','mail.thread']


    journal_id = fields.Many2one(track_visibility='onchange')
    ref = fields.Char(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    currency_id = fields.Many2one(track_visibility='onchange')
    rate_diff_partial_rec_id = fields.Many2one(track_visibility='onchange')
    line_ids = fields.One2many(track_visibility='onchange')
    partner_id = fields.Many2one(track_visibility='onchange')
    amount = fields.Monetary(track_visibility='onchange')
    # narration = fields.Text(string='Internal Note')
    company_id = fields.Many2one(track_visibility='onchange')
    matched_percentage = fields.Float(track_visibility='onchange')
    statement_line_id = fields.Many2one(track_visibility='onchange')
    dummy_account_id = fields.Many2one(track_visibility='onchange')
    state = fields.Selection(track_visibility='onchange')




