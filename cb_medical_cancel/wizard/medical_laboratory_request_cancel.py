from odoo import fields, models


class MedicalLaboratoryRequestCancel(models.TransientModel):
    _name = "medical.laboratory.request.cancel"
    _inherit = "medical.request.cancel"

    request_id = fields.Many2one("medical.laboratory.request")
