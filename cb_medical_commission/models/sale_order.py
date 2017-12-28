# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_line_agents_data(self, line):
        if line.product_id.medical_commission:
            agent_lines = {}
            for procedure in line.procedure_ids:
                if procedure.commission_agent_id.id not in agent_lines:
                    agent_lines[procedure.commission_agent_id.id] = []
                agent_lines[procedure.commission_agent_id.id].append(procedure)
            return [{
                'agent': x,
                'commission': agent_lines[x][0].commission_agent_id.commission.id,
                'procedure_ids': [(6, 0, [
                    p.id for p in agent_lines[x]
                ])]
            } for x in agent_lines]
        return super(SaleOrder, self)._prepare_line_agents_data(line)
