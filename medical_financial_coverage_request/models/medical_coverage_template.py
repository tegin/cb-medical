from odoo import models, fields


class MedicalCoverageTemplate(models.Model):
    _inherit = 'medical.coverage.template'

    subscriber_required = fields.Boolean(default=False)
    subscriber_format = fields.Char()
