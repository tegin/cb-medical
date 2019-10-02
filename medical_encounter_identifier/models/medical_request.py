from odoo import models


class MedicalRequest(models.AbstractModel):
    _name = "medical.request"
    _inherit = ["medical.request", "medical.cb.identifier"]
