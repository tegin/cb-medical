from odoo import api, models


class MedicalRequest(models.AbstractModel):
    _name = "medical.document.reference"
    _inherit = ["medical.document.reference", "medical.request"]

    @api.model
    def _ignore_child_states(self):
        return True

    def check_state(self):
        return
