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
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_administration_encounter.medical_encounter_action"
        )
        result["views"] = [(False, "form")]
        result["res_id"] = encounter.id
        return result

    def _create_encounter_patient_vals_write(self, patient, patient_vals):
        new_patient_vals = {}
        for field in patient_vals:
            if field not in patient._fields:
                continue
            original_patient_value = patient[field]
            if isinstance(original_patient_value, models.Model):
                original_patient_value = original_patient_value.id
            if patient_vals[field] != original_patient_value:
                new_patient_vals[field] = patient_vals[field]
        return new_patient_vals

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
            new_patient_vals = self._create_encounter_patient_vals_write(
                patient, patient_vals
            )
            if new_patient_vals:
                patient.write(new_patient_vals)
                patient.flush()
        if isinstance(center, int):
            center = self.env["res.partner"].browse(center)
        return self.create(self._create_encounter_vals(patient, center, **kwargs))

    def _create_encounter_vals(self, patient, center, **kwargs):
        return {"patient_id": patient.id, "center_id": center.id}
