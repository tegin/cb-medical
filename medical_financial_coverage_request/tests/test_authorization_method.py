# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAuthorizationMethod(TransactionCase):
    def setUp(self):
        super(TestAuthorizationMethod, self).setUp()

    def test_integration(self):
        method = self.env["medical.authorization.method"].create(
            {
                "name": "Method",
                "integration_information": "INFO",
                "code": "DEMO_METHOD",
                "method_information": "INFO",
            }
        )
        web = self.env["medical.authorization.web"].create(
            {"name": "web", "code": "DEMO", "link": "LINK", "notes": "NOTES"}
        )
        self.assertNotEqual(method.integration_information, web.link)
        self.assertNotEqual(method.method_information, web.notes)
        method.authorization_web_id = web
        self.assertEqual(method.integration_information, web.link)
        self.assertEqual(method.method_information, web.notes)
        web.write({"link": "LINK2", "notes": "NOTES2"})
        self.assertEqual(method.integration_information, web.link)
        self.assertEqual(method.method_information, web.notes)
