# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError


class MedicalEncounter(models.AbstractModel):
    _inherit = 'medical.encounter'

    @api.multi
    def recompute_commissions(self):
        for rec in self:
            rec._compute_commissions()
            for sale_order in rec.sale_order_ids:
                if sale_order.state == 'draft' or not sale_order.invoice_ids:
                    sale_order.recompute_lines_agents()
                elif all(i.state == 'draft' for i in sale_order.invoice_ids):
                    sale_order.recompute_lines_agents()
                    sale_order.invoice_ids.recompute_lines_agents()
                else:
                    lines = sale_order.mapped('order_line')
                    for line in lines.mapped('invoice_lines').mapped('agents'):
                        line.change_agent(
                            line.procedure_id.commission_agent_id)

    @api.multi
    def create_sale_order(self):
        res = super().create_sale_order()
        self._compute_commissions()
        for sale_order in self.sale_order_ids:
            sale_order.recompute_lines_agents()
        return res

    def _compute_commissions(self):
        self.ensure_one()
        for pr in self.careplan_ids.mapped('procedure_request_ids'):
            for procedure in pr.procedure_ids:
                procedure.sale_order_line_ids = False
                procedure.compute_commission(pr)
