from odoo import fields, models


class MedicalCareplanCancel(models.TransientModel):
    _name = "medical.careplan.cancel"
    _description = "medical.careplan.cancel"
    _inherit = "medical.request.cancel"

    request_id = fields.Many2one("medical.careplan")
