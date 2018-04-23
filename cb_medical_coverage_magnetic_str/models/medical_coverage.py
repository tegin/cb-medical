# Copyright (C) 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MedicalCoverage(models.Model):
    _inherit = 'medical.coverage'

    subscriber_magnetic_str = fields.Char(readonly=True)
