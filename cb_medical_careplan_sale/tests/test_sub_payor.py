# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMedicalSubPayor(TransactionCase):
    def setUp(self):
        super(TestMedicalSubPayor, self).setUp()
        self.payor = self.env["res.partner"].create(
            {"name": "Payor", "is_payor": True}
        )

    def test_constrain(self):
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(
                {"name": "Sub Payor", "is_sub_payor": True}
            )
