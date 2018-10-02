from odoo import fields, models


class MedicalFlag(models.Model):
    # FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)
    _inherit = 'medical.flag'

    flag = fields.Char(related='category_id.flag', readonly=True)
    level = fields.Selection(related='category_id.level', readonly=True)
