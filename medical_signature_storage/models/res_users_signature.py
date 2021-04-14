# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsersSignature(models.Model):
    _name = "res.users.signature"
    _description = "User Signature"

    user_id = fields.Many2one("res.users", required=True)
    signature = fields.Binary(required=True)
