# -*- coding: utf-8 -*-

from openerp import api, fields, models

class stock_picking_reject_wizard(models.TransientModel):
    _name = 'stock.picking.reject.wizard'
    _description = 'Stock Picking Reject Wizard'

    @api.multi
    def action_wizard_reject_notice(self):
        picking_ids = self.env.context['active_ids']
        msg = self.msg
        pickings = self.env['stock.picking'].browse(picking_ids)
        for pick in pickings :
            pick.action_reject_notice(msg)
        return

    msg = fields.Text(string='Reason for Rejection', required=True)
