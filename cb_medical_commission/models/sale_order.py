# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_line_agents_data(self, line):
        if self.encounter_id and not self.third_party_order:
            res = []
            for procedure in line.procedure_ids:
                res.append({
                    'agent': procedure.commission_agent_id.id,
                    'commission': procedure.commission_agent_id.commission.id,
                    'procedure_id': procedure.id,
                })
            return res
        return super(SaleOrder, self)._prepare_line_agents_data(line)
