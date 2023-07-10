# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    # Make it selection? Or just text of whatever?
    medical_process_description = fields.Text(string="Medical Process Description")
