# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalEncounter(models.Model):
    _name = "medical.encounter"
    _inherit = ["medical.encounter", "mgmtsystem.quality.issue.abstract"]
