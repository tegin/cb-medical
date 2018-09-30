from odoo import fields, models


class MedicalFlag(models.Model):
    # FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)
    _inherit = 'medical.flag.category'
    _description = 'Medical Category Flag'

    flag = fields.Char()
