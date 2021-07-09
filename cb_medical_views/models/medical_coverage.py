from odoo import api, models


class MedicalCoverage(models.Model):
    _inherit = "medical.coverage"

    @api.multi
    @api.depends("subscriber_id", "internal_identifier")
    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (
                    rec.id,
                    rec.subscriber_id or rec.name or rec.internal_identifier,
                )
            )
        return result
