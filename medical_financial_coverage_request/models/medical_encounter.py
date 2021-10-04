# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    @api.model
    def create_encounter(
        self, patient=False, patient_vals=False, center=False, **kwargs
    ):
        encounter = self._create_encounter(
            patient=patient,
            patient_vals=patient_vals,
            center=center,
            **kwargs,
        )
        action = self.env.ref(
            "medical_administration_encounter.medical_encounter_action"
        )
        result = action.read()[0]
        result["views"] = [(False, "form")]
        result["res_id"] = encounter.id
        return result

    @api.model
    def _create_encounter(
        self, patient=False, patient_vals=False, center=False, **kwargs
    ):
        if not patient_vals and not patient:
            raise ValidationError(_("Patient information is required"))
        if not center:
            raise ValidationError(_("Center is required"))
        if not patient_vals:
            patient_vals = {}
        if not patient:
            patient = self.env["medical.patient"].create(patient_vals)
        else:
            if isinstance(patient, int):
                patient = self.env["medical.patient"].browse(patient)
            new_patient_vals = {}
            for field in patient_vals:
                if patient_vals[field] != patient._fields.get(field):
                    new_patient_vals[field] = patient_vals[field]
            if new_patient_vals:
                patient.write(new_patient_vals)
                patient.flush()
        if isinstance(center, int):
            center = self.env["res.partner"].browse(center)
        return self.create(
            self._create_encounter_vals(patient, center, **kwargs)
        )

    def _create_encounter_vals(self, patient, center, **kwargs):
        return {"patient_id": patient.id, "center_id": center.id}
