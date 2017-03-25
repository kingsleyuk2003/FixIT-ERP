# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html

from openerp import api, fields, models, _


class ResCompanyReport(models.Model):
    _inherit = "res.company"

    header_logo = fields.Binary(string='Header Logo')
    footer_banner = fields.Binary(string='Footer Banner')
    footer_data = fields.Html(string='Footer Data')
    header_data = fields.Html(string='Header Data', help="e.g. Addresses of head Office and Tel No should be added here ")
    # logo_text = fields.Text(string='Logo Below Text', help="The text below the logo")
    po_note = fields.Text(string='Purchase Order Note', help="e.g. Terms and Conditions")
    inv_note = fields.Text(string='Invoice Note', help="e.g. Terms and Conditions")
    html_after_header = fields.Html('Html after Header')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _default_note(self):
        return self.env.user.company_id.po_note

    notes = fields.Text('Terms and conditions', default=_default_note)




