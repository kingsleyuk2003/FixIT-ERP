# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import Warning, except_orm



class po_import(models.TransientModel):
    _name = 'po.import.wizard'
    _description = "PO Import"

    input_file = fields.Binary('Import File', required=True)

