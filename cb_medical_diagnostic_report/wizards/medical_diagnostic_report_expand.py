# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDiagnosticReportExpand(models.TransientModel):

    _inherit = "medical.diagnostic.report.expand"
    report_category_id = fields.Many2one(
        "medical.report.category",
        related="diagnostic_report_id.report_category_id",
    )

    def _merge_new_vals(self, vals):

        new_vals = super()._merge_new_vals(vals)

        if (
            vals["with_department"]
            and not self.diagnostic_report_id.with_department
        ):
            new_vals.update(
                {
                    "with_department": vals["with_department"],
                    "medical_department_header": vals[
                        "medical_department_header"
                    ],
                }
            )
        return new_vals
