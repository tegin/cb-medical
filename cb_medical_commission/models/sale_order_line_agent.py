# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrderLineAgent(models.Model):
    _inherit = 'sale.order.line.agent'

    procedure_ids = fields.Many2many(
        'medical.procedure',
        'Procedure'
    )
