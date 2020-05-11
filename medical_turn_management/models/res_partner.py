# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    turn_specialty_ids = fields.Many2many(
        "medical.turn.specialty", string="Specialties", readonly=True
    )
