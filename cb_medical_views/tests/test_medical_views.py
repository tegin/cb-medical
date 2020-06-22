# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMedicalViews(TransactionCase):
    def setUp(self):
        super(TestMedicalViews, self).setUp()
        self.payor = self.env["res.partner"].create(
            {"name": "Test payor", "is_payor": True, "comercial": "Comercial"}
        )
        self.coverage_template = self.env["medical.coverage.template"].create(
            {"name": "test coverage template", "payor_id": self.payor.id}
        )

    def test_name_get(self):
        names = self.payor.with_context(cb_display=True).name_get()
        self.assertEqual(names[0][1], "Comercial")

        names = self.coverage_template.name_get()
        self.assertEqual(
            names[0][1], "(Comercial) Test payor - test coverage template"
        )
