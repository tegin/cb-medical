from odoo import fields, models


class MedicalRequestTrigger(models.Model):
    _name = 'medical.request.trigger'

    request_id = fields.Integer()
    request_model = fields.Text()
    trigger_id = fields.Integer()
    trigger_model = fields.Text()
