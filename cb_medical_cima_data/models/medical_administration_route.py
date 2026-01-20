# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalAdministrationRoute(models.Model):

    _inherit = "medical.administration.route"

    api_id = fields.Integer()
