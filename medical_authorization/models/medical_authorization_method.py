from odoo import fields, models


class MedicalAuthorizationMethod(models.Model):
    _inherit = "medical.authorization.method"

    check_required = fields.Boolean(default=False)
