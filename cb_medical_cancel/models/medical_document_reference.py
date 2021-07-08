from odoo import models


class MedicalDocumentReference(models.Model):
    _inherit = "medical.document.reference"

    def check_cancellable(self):
        return True
