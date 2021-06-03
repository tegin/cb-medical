# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.AbstractModel):
    _inherit = "sale.order"

    encounter_id = fields.Many2one(
        "medical.encounter", readonly=True, index=True
    )
    coverage_id = fields.Many2one("medical.coverage", readonly=True)
    coverage_template_id = fields.Many2one(
        "medical.coverage.template",
        readonly=True,
        related="coverage_id.coverage_template_id",
    )
    coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement", index=True,
    )
    patient_id = fields.Many2one("medical.patient", readonly=True, index=True)

    def create_third_party_move(self):
        if self.coverage_agreement_id:
            return
        return super().create_third_party_move()

    @api.model
    def _prepare_third_party_order(self):
        res = super(SaleOrder, self)._prepare_third_party_order()
        res["encounter_id"] = self.encounter_id.id or False
        res["patient_id"] = self.patient_id.id or False
        return res
