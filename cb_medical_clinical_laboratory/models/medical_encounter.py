# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalEncounter(models.Model):
    _name = "medical.encounter"
    _inherit = ["medical.encounter"]

    laboratory_sample_ids = fields.One2many(
        string="Laboratory Samples",
        comodel_name="medical.laboratory.sample",
        inverse_name="encounter_id",
        readonly=True,
    )
    laboratory_sample_count = fields.Integer(
        compute="_compute_laboratory_sample_count",
        string="# of Samples",
        copy=False,
    )

    @api.depends("laboratory_sample_ids")
    def _compute_laboratory_sample_count(self):
        for rec in self:
            rec.laboratory_sample_count = len(rec.laboratory_sample_ids.ids)

    def action_view_laboratory_samples(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_laboratory.medical_laboratory_sample_action"
        )
        result = action.read()[0]

        result["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_laboratory_request_id": self.id,
            "default_name": self.name,
        }
        result["domain"] = [("encounter_id", "=", self.id)]
        if len(self.laboratory_sample_ids) == 1:
            res = self.env.ref("medical.laboratory.sample.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.laboratory_sample_ids.id
        return result

    @api.constrains("patient_id")
    def _check_patient_events(self):
        if not self.env.context.get("no_check_patient", False):
            if self.laboratory_sample_ids.filtered(
                lambda r: r.patient_id != self.patient_id
            ):
                raise ValidationError(_("Patient inconsistency"))
