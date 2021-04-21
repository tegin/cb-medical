# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDiagnosticReportTemplate(models.Model):

    _inherit = "medical.diagnostic.report.template"

    report_category_id = fields.Many2one(required=True, auto_join=True)
    medical_department_id = fields.Many2one(
        related="report_category_id.medical_department_id"
    )
    medical_department_header = fields.Html(
        related="medical_department_id.diagnostic_report_header", readonly=True
    )

    def _generate_report_vals(self, encounter):
        result = super()._generate_report_vals(encounter)
        result.update(
            {
                "with_department": True
                if self.medical_department_id
                else False,
                "medical_department_header": self.medical_department_header,
                "report_category_id": self.report_category_id.id,
            }
        )
        return result
