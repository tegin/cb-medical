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
    with_department_report_header = fields.Boolean(
        related="medical_department_id.with_department_report_header"
    )

    def _generate_report(self, studies=None, **kwargs):
        report = super()._generate_report(studies=studies, **kwargs)
        if (
            self.report_category_id.import_study_images_automatically
            and studies
        ):
            series = studies.mapped("series_ids").filtered(
                lambda r: r.modality_id
                == self.report_category_id.image_modality_id
            )
            studies.storage_ids.mapped("endpoint_ids")._get_images_from_series(
                report, series
            )
        return report

    def _generate_report_vals(self, studies=None, **kwargs):
        result = super()._generate_report_vals(**kwargs)
        result.update(
            {
                "study_ids": [(6, 0, studies.ids)] if studies else False,
                "with_department": True
                if self.medical_department_id
                else False,
                "medical_department_header": self.medical_department_header
                if self.with_department_report_header
                else False,
                "report_category_id": self.report_category_id.id,
            }
        )
        return result
