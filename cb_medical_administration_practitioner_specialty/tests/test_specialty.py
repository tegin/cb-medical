# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestMedicalCommission(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.specialty = cls.env["medical.specialty"].create(
            {"name": "Trauma", "description": "Traumatology", "code": "TRA"}
        )
        cls.specialty.sequence_number_next = 21
        cls.doctor = cls.env.ref("medical_administration_practitioner.doctor")
        cls.ict = cls.env.ref("medical_administration_practitioner.ict")

    def test_create_practitioner_doctor(self):
        practitoner = self.env["res.partner"].create(
            {
                "name": "Doctor",
                "is_practitioner": True,
                "practitioner_role_id": self.doctor.id,
                "specialty_id": self.specialty.id,
            }
        )
        self.assertEqual(practitoner.practitioner_identifier, "TRA021")
        self.assertEqual(
            practitoner.specialty_id.id, practitoner.specialty_ids.ids[0]
        )
        self.assertEqual(
            practitoner.practitioner_role_id.id,
            practitoner.practitioner_role_ids.ids[0],
        )
        self.specialty._compute_seq_number_next()
        self.assertEqual(self.specialty.sequence_number_next, 22)

        self.assertEqual(self.specialty, practitoner.specialty_ids)

    def test_create_practitioner_doctor_search(self):
        practitoner = self.env["res.partner"].create(
            {
                "name": "Doctor",
                "is_practitioner": True,
                "practitioner_role_ids": [(4, self.doctor.id)],
                "specialty_ids": [(4, self.specialty.id)],
            }
        )
        self.assertEqual(self.specialty, practitoner.specialty_id)
        pracs = self.env["res.partner"].search(
            [("specialty_id", "=", self.specialty.id)]
        )
        self.assertEqual(pracs, practitoner)

    def test_create_practitioner_it(self):
        practitoner = self.env["res.partner"].create(
            {
                "name": "Doctor",
                "is_practitioner": True,
                "practitioner_role_ids": [(4, self.ict.id)],
            }
        )
        self.assertNotEqual(practitoner.practitioner_identifier, "TRA021")
        self.assertRegex(practitoner.practitioner_identifier, r"^PRA.*$")
        self.assertEqual(self.ict, practitoner.practitioner_role_id)
        self.assertEqual(self.ict, practitoner.practitioner_role_ids)

    def test_constrain_01(self):
        practitoner = self.env["res.partner"].create(
            {
                "name": "Doctor",
                "is_practitioner": True,
                "practitioner_role_id": self.doctor.id,
                "specialty_id": self.specialty.id,
            }
        )
        with self.assertRaises(ValidationError):
            practitoner.practitioner_role_ids |= self.ict
