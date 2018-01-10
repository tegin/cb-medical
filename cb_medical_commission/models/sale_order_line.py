# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def compute_procedure(self):
        return self.env['medical.procedure'].search([
            ('sale_order_line_ids', '=', self.id)
        ])

    @api.model
    def prepare_sale_order_line_agent(self, agent):
        return [{
            'agent': agent.id,
            'commission': agent.commission.id,
        }]
