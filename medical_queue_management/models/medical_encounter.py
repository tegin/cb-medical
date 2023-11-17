# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    queue_token_id = fields.Many2one("queue.token", readonly=True)

    def _generate_token_vals(self):
        return {}

    def _get_queue_token(self):
        self.ensure_one()
        if not self.queue_token_id:
            self.queue_token_id = self.env["queue.token"].create(
                self._generate_token_vals()
            )
        return self.queue_token_id
