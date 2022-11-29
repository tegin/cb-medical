# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalCoverage(models.Model):

    _inherit = "medical.coverage"

    subscriber_magnetic_str = fields.Char(readonly=True)
