# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import timedelta


class WzdMedicalTurn(models.TransientModel):

    _name = 'wzd.medical.turn'

    turn_specialty_ids = fields.Many2many(
        'medical.turn.specialty',
    )
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    def _get_specialties(self):
        if self.turn_specialty_ids:
            return self.turn_specialty_ids
        return self.env['medical.turn.specialty'].search([])

    @api.multi
    def doit(self):
        self.ensure_one()
        specialties = self._get_specialties()
        specialties._execute_rules(
            fields.Date.from_string(self.start_date),
            fields.Date.from_string(self.end_date) + timedelta(days=1)
        )
        return {}
