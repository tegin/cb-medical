from odoo import api, models


class MedicalDocumentReference(models.Model):
    _inherit = "medical.document.reference"

    def check_cancellable(self):
        return True

    @api.model
    def cancellation_domain(self):
        return []

    def cancel(self):
        result = super().cancel()
        # Document references are not cancellable,
        # so we remove the link to the parent to leave it
        self.write({"parent_id": False, "parent_model": False})
        return result
