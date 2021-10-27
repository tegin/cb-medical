# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalEncounterCreateDiagnosticReport(models.TransientModel):

    _inherit = "medical.encounter.create.diagnostic.report"

    @api.model
    def _default_studies(self):
        return []

    template_id = fields.Many2one(
        domain="['|',('medical_department_id','=',False),"
        "('medical_department_id.user_ids','=',uid)]"
    )
    image_modality_id = fields.Many2one(
        related="template_id.report_category_id.image_modality_id"
    )
    study_ids = fields.Many2many(
        "medical.imaging.study",
        default=lambda r: r._default_studies(),
        relation="encounter_create_diagnostic_report_study_rel",
    )

    def _generate_kwargs(self):
        res = super()._generate_kwargs()
        res["studies"] = self.study_ids
        return res
