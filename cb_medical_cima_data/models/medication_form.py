# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicationForm(models.Model):

    _inherit = "medication.form"

    api_id = fields.Integer()
