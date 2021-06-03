# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMedicalLocation(TransactionCase):
    def test_center(self):
        vals = {
            "name": "reception",
            "description": "location_description",
            "is_reception": True,
        }
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(vals)
        center_vals = {
            "name": "test name",
            "description": "test description",
            "is_center": True,
        }
        center = self.env["res.partner"].create(center_vals)
        self.assertTrue(center.is_center)
        self.assertTrue(center.center_identifier)
        self.assertEqual(center.reception_count, 0)
        vals["center_id"] = center.id
        location = self.env["res.partner"].create(vals)
        self.assertTrue(location.is_reception)
        self.assertEqual(center.reception_count, 1)
        self.assertEqual(center.location_count, 0)
        self.env["res.partner"].create(
            {"name": "Location", "is_location": True, "center_id": center.id}
        )
        self.assertEqual(center.reception_count, 1)
        self.assertEqual(center.location_count, 1)
