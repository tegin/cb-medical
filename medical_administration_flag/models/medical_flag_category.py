from odoo import fields, models


class MedicalFlag(models.Model):
    # FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)
    _name = 'medical.flag.category'
    _description = 'Medical Category Flag'

    name = fields.Char(required=True)
    description = fields.Text()
