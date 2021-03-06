# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# © 2015 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openerp import fields, models


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    operating_unit_ids = fields.Many2many(
        comodel_name='operating.unit', string='Operating Units',
        relation='analytic_account_operating_unit_rel',
        column1='analytic_account_id',
        column2='operating_unit_id')
