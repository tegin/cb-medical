# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    administrative_document_ids = fields.One2many(
        "medical.document.reference",
        inverse_name="patient_id",
        domain=[
            ("document_kind", "=", "administrative"),
            ("autogenerated", "=", False),
        ],
        readonly=True,
    )
    medical_document_ids = fields.One2many(
        "medical.document.reference",
        inverse_name="patient_id",
        domain=[("document_kind", "=", "medical"), ("autogenerated", "=", False)],
        readonly=True,
    )
    autogenerated_document_ids = fields.One2many(
        "medical.document.reference",
        inverse_name="patient_id",
        domain=[("autogenerated", "=", True)],
        readonly=True,
    )
