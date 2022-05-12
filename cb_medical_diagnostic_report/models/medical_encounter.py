# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"
    _description = "Medical Encounter"

    study_ids = fields.One2many(
        comodel_name="medical.imaging.study", inverse_name="encounter_id"
    )
