# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalLaboratoryEvent(models.Model):
    _inherit = "medical.laboratory.event"

    def get_sale_order_line_vals(self, is_insurance):
        vals = super().get_sale_order_line_vals(is_insurance)
        if is_insurance:
            cov = (
                self.laboratory_request_id.careplan_id.coverage_id.coverage_template_id
            )
            vals["coverage_agreement_item_id"] = (
                self.env["medical.coverage.agreement.item"]
                .get_item(
                    self.service_id, cov, self.laboratory_request_id.center_id
                )
                .id
            )
        return vals

    def _change_authorization(self, vals, **kwargs):
        res = super()._change_authorization(vals, **kwargs)
        if self.mapped("sale_order_line_ids"):
            self.mapped("sale_order_line_ids").filtered(
                lambda r: not r.is_private
            ).write(vals)
        return res
