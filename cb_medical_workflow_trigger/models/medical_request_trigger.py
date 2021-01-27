from odoo import fields, models


class MedicalRequestTrigger(models.Model):
    _name = "medical.request.trigger"
    _description = "medical.request.trigger"

    request_id = fields.Integer(index=True)
    request_model = fields.Text(index=True)
    trigger_id = fields.Integer(index=True)
    trigger_model = fields.Text(index=True)
