# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    surgical_encounter_ids = fields.One2many(
        "medical.encounter",
        "patient_id",
        string="Surgical Encounters",
        domain=[("is_surgery_process", "=", True)],
    )
