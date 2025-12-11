# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResUsersUpdateSignature(models.TransientModel):

    _name = "res.users.update.signature"
    _description = "Update signature"

    user_id = fields.Many2one("res.users", required=True)
    option = fields.Selection(
        [("signature", "Signature"), ("file", "File"), ("clear", "Clear")],
        required=True,
        default="signature",
    )
    signature = fields.Binary()
    signature_file = fields.Binary()
    signature_file_name = fields.Char()
    full_name = fields.Text(compute="_compute_full_name")

    @api.depends("user_id")
    def _compute_full_name(self):
        for record in self:
            record.full_name = record._get_full_name()

    def _get_full_name(self):
        return self.user_id.display_name

    def update_signature(self):
        self.ensure_one()
        if self.option == "clear":
            self.user_id.current_signature_id = False
            return
        signature = self.env["res.users.signature"].create(
            self._create_signature_vals()
        )
        self.user_id.current_signature_id = signature

    def _create_signature_vals(self):
        result = {
            "user_id": self.user_id.id,
        }
        if self.option == "signature":
            result["signature"] = self.signature
        if self.option == "file":
            # TODO: Validate the file is an image
            result["signature"] = self.signature_file
        return result
