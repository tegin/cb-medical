# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _prepare_line_agents_data(self, line):
        rec = super(AccountInvoice, self)._prepare_line_agents_data(line)
        if line.sale_line_ids:
            sale_line = line.sale_line_ids[0]
            if sale_line.product_id.medical_commission:
                agent_lines = {}
                for pr in sale_line.request_group_id.procedure_request_ids:
                    for procedure in pr.procedure_ids:
                        agent = procedure.commission_agent_id
                        agent_lines[agent.id] = agent.commission.id
                rec = [{
                    'agent': x,
                    'commission': agent_lines[x]} for x in agent_lines]
            return rec
