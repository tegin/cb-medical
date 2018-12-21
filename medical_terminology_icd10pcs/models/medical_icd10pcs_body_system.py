# Copyright 2018 Creu Blacna
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalIcd10pcsSystem(models.Model):

    _name = 'medical.icd10pcs.body.system'
    _description = 'Medical Icd10pcs System'

    code = fields.Char(required=True)
    name = fields.Char(translate=True)
    section_id = fields.Many2one(
        'medical.icd10pcs.section',
        required=True,
    )
