# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalPatientAddDocument(models.TransientModel):

    _name = "medical.patient.add.document"

    document_type_id = fields.Many2one(
        "medical.document.type",
        required=True,
        domain=[("storage_backend_id", "!=", False)],
        required=True,
    )
    data = fields.Binary(required=True)
    patient_id = fields.Many2one("medical.patient", required=True)

    @api.multi
    def doit(self):
        self.ensure_one()
        self.patient_id._add_scanned_document(
            data=self.data, document_type=self.document_type_id
        )
