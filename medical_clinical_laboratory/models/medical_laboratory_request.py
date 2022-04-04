# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalLaboratoryRequest(models.Model):
    # FHIR Entity: Procedure request
    # (https://www.hl7.org/fhir/procedurerequest.html)
    _name = "medical.laboratory.request"
    _description = "Laboratory Request"
    _inherit = "medical.request"

    internal_identifier = fields.Char(string="Laboratory request")
    laboratory_event_ids = fields.One2many(
        string="Laboratory Events",
        comodel_name="medical.laboratory.event",
        inverse_name="laboratory_request_id",
        readonly=True,
    )
    laboratory_event_count = fields.Integer(
        compute="_compute_laboratory_event_count",
        string="# of Events",
        copy=False,
    )

    @api.depends("laboratory_event_ids")
    def _compute_laboratory_event_count(self):
        for rec in self:
            rec.laboratory_event_count = len(rec.laboratory_event_ids.ids)

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.laboratory.request")
            or "/"
        )

    def _get_parent_field_name(self):
        return "laboratory_request_id"

    def action_view_request_parameters(self):
        return {
            "view": "medical_clinical_laboratory."
            "medical_laboratory_request_action",
            "view_form": "medical.procedure.request.view.form",
        }

    def action_view_laboratory_events(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_laboratory.medical_laboratory_event_action"
        )
        result = action.read()[0]
        result["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_performer_id": self.performer_id.id,
            "default_laboratory_request_id": self.id,
            "default_name": self.name,
        }
        result["domain"] = [("laboratory_request_id", "=", self.id)]
        if len(self.laboratory_event_ids) == 1:
            res = self.env.ref("medical.laboratory.event.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.laboratory_event_ids.id
        return result

    @api.constrains("patient_id")
    def _check_patient_events(self):
        if not self.env.context.get("no_check_patient", False):
            if self.laboratory_event_ids.filtered(
                lambda r: r.patient_id != self.patient_id
            ):
                raise ValidationError(_("Patient inconsistency"))

    def _generate_sample_domain(self):
        return [("encounter_id", "=", self.encounter_id.id)]

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._generate_sample()
        return records

    def _generate_sample(self):
        sample = self.env["medical.laboratory.sample"].search(
            self._generate_sample_domain(), limit=1
        )
        if not sample:
            sample = self.env["medical.laboratory.sample"].create(
                self._generate_sample_vals()
            )
        return sample

    def _generate_sample_vals(self):
        return {
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id,
            "service_id": self.service_id.id,
            "performer_id": self.performer_id.id,
        }
