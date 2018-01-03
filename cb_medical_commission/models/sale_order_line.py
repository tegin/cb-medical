# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def compute_procedure(self):
        procedures = self.procedure_request_id.procedure_ids
        for pr in self.request_group_id.procedure_request_ids:
            procedures += pr.procedure_ids
        return procedures

    @api.model
    def prepare_sale_order_line_agent(self, agent):
        return [{
            'agent': agent.id,
            'commission': agent.commission.id,
        }]
