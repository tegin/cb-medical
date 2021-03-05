# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsersSignature(models.Model):
    # TODO: Improve security
    _name = "res.users.signature"
    _description = "Res Users Signature"  # TODO

    user_id = fields.Many2one(required=True)
    signature = fields.Binary(required=True)
