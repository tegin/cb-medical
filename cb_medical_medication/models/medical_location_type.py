from odoo import fields, models


class MedicalLocationType(models.Model):
    _name = 'medical.location.type'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(required=True, default=True)
