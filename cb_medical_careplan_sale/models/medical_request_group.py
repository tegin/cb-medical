# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalRequestGroup(models.Model):
    _inherit = "medical.request.group"

    def compute_price(self, is_insurance):
        if self.child_model and self.child_id:
            return (
                self.env[self.child_model]
                .browse(self.child_id)
                .compute_price(is_insurance)
            )
        return super(MedicalRequestGroup, self).compute_price(is_insurance)

    @api.depends(
        "is_billable",
        "sale_order_line_ids",
        "coverage_agreement_item_id",
        "state",
        "child_model",
        "child_id",
    )
    def _compute_is_sellable(self):
        super()._compute_is_sellable()

    def check_sellable(self, is_insurance, agreement_item):
        if self.child_model and self.child_id:
            return (
                self.env[self.child_model]
                .browse(self.child_id)
                .check_sellable(is_insurance, agreement_item)
            )
        return super().check_sellable(is_insurance, agreement_item)
