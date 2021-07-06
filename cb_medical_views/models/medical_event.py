from odoo import api, models


class MedicalEvent(models.AbstractModel):
    _inherit = "medical.event"

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.internal_identifier))
        return result
