from odoo import fields, models


class MedicalProcedureRequestCancel(models.TransientModel):
    _name = "medical.procedure.request.cancel"
    _inherit = "medical.request.cancel"

    request_id = fields.Many2one("medical.procedure.request")
