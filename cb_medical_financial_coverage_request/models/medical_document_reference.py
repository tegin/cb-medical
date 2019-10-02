from odoo import api, models


class MedicalDocumentReference(models.Model):
    _inherit = "medical.document.reference"

    @api.depends("state")
    def _compute_can_deactivate(self):
        for record in self:
            record.can_deactivate = True
