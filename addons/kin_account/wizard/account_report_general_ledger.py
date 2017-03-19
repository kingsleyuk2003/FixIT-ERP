# -*- coding: utf-8 -*-

from openerp import fields, models, _
from openerp.exceptions import UserError


class AccountReportGeneralLedgerExtend(models.TransientModel):
    _inherit = "account.report.general.ledger"

    account_ids = fields.Many2many('account.account', string='Accounts', help="filter by GL accounts")

    def _print_report(self, data):
        data = self.pre_print_report(data)

        account_ids =  [account.id for account in self.account_ids]
        data['form'].update({'account_ids': account_ids})

        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        action = self.env['report'].with_context(landscape=True).get_action(self, 'account.report_generalledger', data=data)
        return action