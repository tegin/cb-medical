from odoo import fields, models


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    authorization_checked = fields.Boolean(
        default=False,
        readonly=True,
    )
