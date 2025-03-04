# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    turn_specialty_ids = fields.Many2many(
        "medical.turn.specialty", string="Turn Specialties"
    )

    is_medical_configurator = fields.Boolean(
        compute="_compute_is_medical_configurator", store=False
    )

    @api.depends_context("uid")
    def _compute_is_medical_configurator(self):
        self.is_officer = self.env.user.has_group(
            "medical_base.group_medical_configurator"
        )
