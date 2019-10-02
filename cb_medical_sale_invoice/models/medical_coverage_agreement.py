from odoo import fields, models


class MedicalCoverageAgreement(models.Model):
    _inherit = "medical.coverage.agreement"

    file_reference = fields.Char()
    discount = fields.Float(
        default=0.0, help="General discount applied on the final invoices"
    )
