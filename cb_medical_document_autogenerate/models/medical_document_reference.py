# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDocumentReference(models.Model):

    _inherit = "medical.document.reference"

    autogenerated = fields.Boolean(default=False, readonly=True)
    document_type_id = fields.Many2one(auto_join=True)
    document_kind = fields.Selection(related="document_type_id.kind")
    storage_file_id = fields.Many2one("storage.file", readonly=True)

    # TODO: Add SQL Restriction of autogenerated, storage_file_id must be defined
    # and state cannot be draft

    def _render(self):
        if self.autogenerated:
            return super()._render()
        return self.storage_file_id.data, self.storage_id.mimetype

    def view_action(self):
        if self.autogenerated:
            return super().view_action()
        raise Exception
