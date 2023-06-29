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

    def _add_scanned_document(self, data=b"", document_type_id=False, **vals):
        storage_file = self.env["storage.file"].create({"data": data})
        new_vals = vals.copy()
        new_vals.update(
            {
                "storage_file_id": storage_file.id,
                "fhir_state": "current",
                "patient_id": self.id,
                "document_type_id": document_type_id,
            }
        )
        return self.env["document.reference"].create(new_vals)
