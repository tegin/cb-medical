# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WizardCreateNonconformity(models.TransientModel):
    _name = "wizard.create.nonconformity.encounter"
    _inherit = "wizard.create.nonconformity"
    _description = "Create Issue for encounter"

    def _default_partner(self):
        encounter = self.env[self.env.context.get("active_model")].browse(
            self.env.context.get("active_id")
        )
        return encounter.patient_id.partner_id

    origin_id = fields.Many2one(
        domain=[
            ("from_encounter", "=", True),
            "|",
            ("responsible_user_id", "!=", False),
            ("manager_user_id", "!=", False),
        ]
    )
    partner_id = fields.Many2one(default=lambda r: r._default_partner())
