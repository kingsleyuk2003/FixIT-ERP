# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html

from openerp import api, fields, models, _

class StockPickingAgary(models.Model):
    _inherit = "stock.picking"

    grn_no = fields.Char(string='GRN No.')
    date_grn = fields.Date(string='Date')
    order_no_waybill = fields.Char('Order No. / Way Bill No')
    invoice_no = fields.Char(string="Invoice No.")
    po_no = fields.Char(string="P.O. No.")
    agent_id = fields.Many2one('res.partner',string='Name of Agent')
    driver_id = fields.Many2one('res.partner',string='Name of Driver')
    tel_mobile = fields.Char(string='Tel./Mobile No.')
    container_no = fields.Char(string='Container No.')
    vehicle_no = fields.Char(string='Vehicle No.')




