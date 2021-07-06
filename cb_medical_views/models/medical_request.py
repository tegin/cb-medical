from odoo import api, models


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.internal_identifier))
        return result
