from odoo import fields, models


class MedicalCoverageTemplate(models.Model):
    _inherit = "medical.coverage.template"

    subscriber_required = fields.Boolean(track_visibility=True, default=False)
    subscriber_format = fields.Char(track_visibility=True)
    subscriber_information = fields.Char(
        help="Information useful to find the subscriber value"
    )
