from odoo import fields, models


class MedicalRequestGroupCancel(models.TransientModel):
    _name = "medical.request.group.cancel"
    _inherit = "medical.request.cancel"
    _description = "medical.request.group.cancel"

    request_id = fields.Many2one("medical.request.group")
