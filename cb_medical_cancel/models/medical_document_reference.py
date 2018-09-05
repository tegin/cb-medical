from odoo import api, models


class MedicalDocumentReference(models.Model):
    _inherit = 'medical.document.reference'

    @api.multi
    def check_cancellable(self):
        return True
