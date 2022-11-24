from odoo import api, fields, models


class MedicalFlag(models.Model):
    # FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)
    _inherit = "medical.flag.category"
    _description = "Medical Category Flag"

    flag = fields.Char(compute="_compute_flag", store=True)
    icon = fields.Char()
    level = fields.Selection(
        [("1", "Low"), ("2", "Moderate"), ("3", "High"), ("4", "Critical")],
        required=True,
        default="1",
    )

    @api.model
    def color_mapping(self):
        return {
            "1": "text-success",
            "2": "text-muted",
            "3": "text-warning",
            "4": "text-danger",
        }

    def _get_color(self):
        return

    @api.depends("icon", "level")
    def _compute_flag(self):
        for r in self:
            r.flag = "{} {}".format(r.icon or "", self.color_mapping()[r.level])
