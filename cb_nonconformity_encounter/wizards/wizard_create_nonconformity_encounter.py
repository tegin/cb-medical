# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WizardCreateNonconformity(models.TransientModel):
    _name = "wizard.create.nonconformity.encounter"
    _inherit = "wizard.create.nonconformity"
    _description = "Create Issue for encounter"

    origin_id = fields.Many2one(
        domain=[
            ("from_encounter", "=", True),
            "|",
            ("responsible_user_id", "!=", False),
            ("manager_user_id", "!=", False),
        ]
    )
