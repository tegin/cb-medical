# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemNonconformityOrigin(models.Model):

    _inherit = "mgmtsystem.nonconformity.origin"

    from_encounter = fields.Boolean()

    responsible_user_id = fields.Many2one(
        "res.users", string="Default Responsible"
    )
    manager_user_id = fields.Many2one("res.users", string="Default Manager")
