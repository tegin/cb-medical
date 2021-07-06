from odoo import api, models


class MedicalCoverageTemplate(models.Model):
    _inherit = "medical.coverage.template"

    @api.depends("name", "internal_identifier", "payor_id.display_name")
    def name_get(self):
        result = []
        for rec in self:
            name = "{payor} - {name}".format(
                name=rec.name,
                payor=rec.payor_id.display_name,
                internal_identifier=rec.internal_identifier,
            )
            result.append((rec.id, name))
        return result
