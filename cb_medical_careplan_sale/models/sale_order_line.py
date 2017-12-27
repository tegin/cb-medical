# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrderLine(models.AbstractModel):
    _inherit = 'sale.order.line'

    careplan_id = fields.Many2one(
        'medical.careplan',
        readonly=True,
    )

    procedure_request_id = fields.Many2one(
        'medical.procedure.request',
        readonly=True,
    )

    request_group_id = fields.Many2one(
        'medical.request.group',
        readonly=True,
    )
