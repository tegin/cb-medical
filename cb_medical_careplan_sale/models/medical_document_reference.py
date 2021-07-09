from odoo import models


class MedicalDocumentReference(models.Model):
    _inherit = "medical.document.reference"

    def check_is_billable(self):
        return self.is_billable
