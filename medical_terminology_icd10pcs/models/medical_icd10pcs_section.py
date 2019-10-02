# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalIcd10pcsSection(models.Model):

    _name = "medical.icd10pcs.section"
    _description = "Medical Icd10pcs Section"

    code = fields.Char(required=True)
    name = fields.Char(translate=True)
