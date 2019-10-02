from odoo import fields, models


class MedicalCoverageTemplate(models.Model):
    _inherit = "medical.coverage.template"

    laboratory_code = fields.Char(track_visibility="onchange")
