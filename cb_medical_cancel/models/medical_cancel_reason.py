from odoo import fields, models


class MedicalCancelReason(models.Model):
    _name = "medical.cancel.reason"
    _description = "Cancellation reason"

    name = fields.Char(required=True)
    description = fields.Char()
    active = fields.Boolean(required=True, default=True)
