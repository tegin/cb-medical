# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import tools
from odoo.tests.common import TransactionCase


class TestSignStorage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.user_id = self.env["res.users"].create(
            {"name": "User", "login": "user_signature_storage"}
        )

    def test_signature(self):
        self.assertFalse(self.user_id.current_signature_id)
        self.assertFalse(
            self.env["res.users.signature"].search([("user_id", "=", self.user_id.id)])
        )
        action = self.user_id.update_signature()
        file = tools.file_open(
            "icon.png",
            mode="rb",
            subdir="addons/medical_signature_storage/static/description",
        ).read()
        self.env[action["res_model"]].with_context(action["context"]).create(
            {"option": "signature", "signature": file}
        ).update_signature()
        self.assertTrue(self.user_id.current_signature_id)

        initial_signature = self.env["res.users.signature"].search(
            [("user_id", "=", self.user_id.id)]
        )
        self.assertEqual(1, len(initial_signature))
        self.assertEqual(initial_signature, self.user_id.current_signature_id)
        self.env[action["res_model"]].with_context(action["context"]).create(
            {
                "option": "file",
                "signature_file": file,
                "signature_file_name": "icon.png",
            }
        ).update_signature()
        self.assertTrue(self.user_id.current_signature_id)
        historic_signatures = self.env["res.users.signature"].search(
            [("user_id", "=", self.user_id.id)]
        )
        self.assertEqual(2, len(historic_signatures))
        self.assertIn(initial_signature, historic_signatures)
        current_signature = historic_signatures - initial_signature
        self.assertEqual(current_signature, self.user_id.current_signature_id)
        self.env[action["res_model"]].with_context(action["context"]).create(
            {"option": "clear"}
        ).update_signature()
        historic_signatures = self.env["res.users.signature"].search(
            [("user_id", "=", self.user_id.id)]
        )
        self.assertEqual(2, len(historic_signatures))
        self.assertFalse(self.user_id.current_signature_id)
