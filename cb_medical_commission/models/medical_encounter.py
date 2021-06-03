# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalEncounter(models.AbstractModel):
    _inherit = "medical.encounter"

    @api.multi
    def recompute_commissions(self):
        for rec in self:
            rec._compute_commissions()
        return True

    @api.multi
    def create_sale_order(self):
        res = super().create_sale_order()
        self._compute_commissions()
        return res

    def _compute_commissions(self):
        self.ensure_one()
        for pr in self.careplan_ids.mapped("procedure_request_ids"):
            for procedure in pr.procedure_ids:
                procedure.compute_commission(pr)
        for request in self.careplan_ids.mapped("laboratory_request_ids"):
            request.compute_commission(request)
        for event in self.careplan_ids.mapped("laboratory_request_ids").mapped(
            "laboratory_event_ids"
        ):
            event.compute_commission()
