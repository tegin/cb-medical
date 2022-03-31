# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


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
