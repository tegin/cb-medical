# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalLaboratorySample(models.Model):
    _name = "medical.laboratory.sample"
    _inherit = "medical.request"
    _description = "Medical Laboratory Sample"

    laboratory_event_ids = fields.One2many(
        string="Laboratory Events",
        comodel_name="medical.laboratory.event",
        inverse_name="laboratory_sample_id",
        readonly=True,
    )
    laboratory_event_count = fields.Integer(
        compute="_compute_laboratory_event_count",
        string="# of Events",
        copy=False,
    )
    encounter_id = fields.Many2one(
        comodel_name="medical.encounter",
        ondelete="restrict",
        index=True,
        readonly=True,
    )

    def draft2active_values(self):
        return {"state": "active"}

    def draft2active(self):
        self.write(self.draft2active_values())

    def active2suspended_values(self):
        return {"state": "suspended"}

    def active2suspended(self):
        self.write(self.active2suspended_values())

    def active2completed_values(self):
        return {"state": "completed"}

    def active2completed(self):
        self.write(self.active2completed_values())

    def active2error_values(self):
        return {"state": "entered-in-error"}

    def active2error(self):
        self.write(self.active2error_values())

    def reactive_values(self):
        return {"state": "active"}

    def reactive(self):
        self.write(self.reactive_values())

    def cancel_values(self):
        return {"state": "cancelled"}

    def cancel(self):
        self.write(self.cancel_values())

    # LABORATORY EVENT RELATED
    @api.depends("laboratory_event_ids")
    def _compute_laboratory_event_count(self):
        for rec in self:
            rec.laboratory_event_count = len(rec.laboratory_event_ids.ids)

    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.laboratory.sample") or "/"

    def _get_parent_field_name(self):
        return "laboratory_sample_id"

    def action_view_request_parameters(self):
        return {
            "view": "medical_clinical_laboratory." "medical_laboratory_sample_action",
            "view_form": "medical.procedure.sample.view.form",
        }

    def _get_event_values(self, vals=False):
        result = {
            "performer_id": self.performer_id.id or False,
            "service_id": self.service_id.id or False,
        }
        result.update(vals or {})
        result.update(
            {
                "laboratory_sample_id": self.id,
                "patient_id": self.patient_id.id,
            }
        )
        return result

    def generate_event(self, vals=False):
        self.ensure_one()
        return self.env["medical.laboratory.event"].create(self._get_event_values(vals))

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
        result["domain"] = "[('laboratory_sample_id', '=', " + str(self.id) + ")]"
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
