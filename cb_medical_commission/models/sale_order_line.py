# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    procedure_ids = fields.Many2many(
        'medical.procedure',
        'sale_order_line_procedure',
        'sale_order_line_id',
        'procedure_id',
        'Procedures'
    )

    @api.model
    def prepare_sale_order_line_agent(self, agent):
        return [{
            'agent': agent.id,
            'commission': agent.commission.id,
        }]
