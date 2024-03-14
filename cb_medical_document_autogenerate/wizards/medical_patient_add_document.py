# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalPatientAddDocument(models.TransientModel):

    _name = "medical.patient.add.document"

    document_type_id = fields.Many2one(
        "medical.document.type",
        required=True,
        domain=[("storage_backend_id", "!=", False)],
    )
    data = fields.Binary(required=True)
    filename = fields.Char(required=True)
    patient_id = fields.Many2one("medical.patient", required=True)

    def doit(self):
        self.ensure_one()
        self.patient_id._add_scanned_document(
            data=self.data, document_type=self.document_type_id, filename=self.filename
        )
