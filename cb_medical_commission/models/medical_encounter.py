# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalEncounter(models.AbstractModel):
    _inherit = 'medical.encounter'

    @api.multi
    def recompute_commissions(self):
        for rec in self:
            for pr in rec.careplan_ids.mapped('procedure_request_ids'):
                for procedure in pr.procedure_ids:
                    procedure.sale_order_line_ids = False
                    procedure.compute_commission(pr)
            for sale_order in rec.sale_order_ids:
                sale_order.recompute_lines_agents()
