# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    current_signature_id = fields.Many2one(
        "res.users.signature", readonly=True
    )
    digital_signature = fields.Binary(
        related="current_signature_id.signature", readonly=True
    )

    def update_signature(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_signature_storage.res_users_update_signature_act_window"
        ).read()[0]
        action["context"] = {
            "default_user_id": self.id,
        }
        return action
