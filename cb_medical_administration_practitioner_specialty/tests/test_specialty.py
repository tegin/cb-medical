# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestMedicalCommission(TransactionCase):
    def setUp(self):
        super(TestMedicalCommission, self).setUp()
        self.specialty = self.env["medical.specialty"].create(
            {"name": "Trauma", "description": "Traumatology", "code": "TRA"}
        )
        self.doctor = self.browse_ref(
            "medical_administration_practitioner.doctor"
        )

    def test_create_practitioner(self):
        self.specialty.sequence_number_next = 21
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
