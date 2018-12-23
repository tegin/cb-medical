from odoo import fields, models


class MedicalCoverageAgreement(models.Model):
    _inherit = 'medical.coverage.agreement'

    file_reference = fields.Char()
