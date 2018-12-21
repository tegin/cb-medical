# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalIcd10pcsBodyPart(models.Model):

    _name = 'medical.icd10pcs.body.part'
    _description = 'Medical Icd10pcs Body Part'

    code = fields.Char(required=True)
    name = fields.Char(translate=True)
    body_system_id = fields.Many2one(
        'medical.icd10pcs.body.system',
        required=True,
    )
    section_id = fields.Many2one(
        'medical.icd10pcs.section',
        realated='body_system_id.section_id',
        readonly=True,
        store=True,
    )
