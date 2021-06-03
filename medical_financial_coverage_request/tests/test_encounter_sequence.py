# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCoverage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})

    def test_write_sequence(self):
        center = self.env["res.partner"].create(
            {"name": "Center", "is_center": True}
        )
        self.assertFalse(center.encounter_sequence_id)
        with self.assertRaises(ValidationError):
            self.env["medical.encounter"].create(
                {"patient_id": self.patient.id, "center_id": center.id}
            )
        center.write({"encounter_sequence_prefix": "R"})
        self.assertEqual(center.encounter_sequence_id.prefix, "R")
        self.assertTrue(center.encounter_sequence_id)
        code = center.encounter_sequence_id.get_next_char(
            center.encounter_sequence_id.number_next_actual
        )
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id, "center_id": center.id}
        )
        self.assertEqual(encounter.internal_identifier, code)

    def test_create_sequence(self):
        center = self.env["res.partner"].create(
            {
                "name": "Center",
                "is_center": True,
                "encounter_sequence_prefix": "S",
            }
        )
        self.assertTrue(center.encounter_sequence_id)
        self.assertEqual(center.encounter_sequence_id.prefix, "S")
        current = center.encounter_sequence_id.number_next_actual
        code = center.encounter_sequence_id.get_next_char(current)
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id, "center_id": center.id}
        )
        self.assertEqual(encounter.internal_identifier, code)
        center.write({"encounter_sequence_prefix": "R"})
        self.assertEqual(center.encounter_sequence_id.prefix, "R")
        self.assertTrue(center.encounter_sequence_id)
        code = center.encounter_sequence_id.get_next_char(current + 1)
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id, "center_id": center.id}
        )
        self.assertEqual(encounter.internal_identifier, code)
