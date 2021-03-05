# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsersUpdateSignature(models.TransientModel):

    _name = "res.users.update.signature"

    user_id = fields.Many2one("res.users", required=True)
    option = fields.Selection(
        [("signature", "Signature"), ("file", "File"), ("clear", "Clear")],
        required=True,
        default="signature",
    )
    signature = fields.Binary()
    signature_file = fields.Binary()
    signature_file_name = fields.Char()

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
