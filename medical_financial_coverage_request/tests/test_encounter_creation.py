from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestEncounterCreate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.center = cls.env["res.partner"].create(
            {
                "is_center": True,
                "name": "Center",
                "encounter_sequence_prefix": "1",
            }
        )
        cls.patient = cls.env["medical.patient"].create(
            {"name": "Demo Patient"}
        )

    def test_create_encounter_constrain_01(self):
        with self.assertRaises(ValidationError):
            self.env["medical.encounter"].create_encounter(
                center=self.center,
            )

    def test_create_encounter_constrain_02(self):
        with self.assertRaises(ValidationError):
            self.env["medical.encounter"].create_encounter(
                patient=self.patient.id,
            )

    def test_create_encounter_constrain_03(self):
        with self.assertRaises(ValidationError):
            self.env["medical.encounter"].create_encounter(
                patient=self.patient,
            )

    def test_create_encounter_id(self):
        encounter_action = self.env["medical.encounter"].create_encounter(
            patient=self.patient.id, center=self.center.id
        )
        encounter = self.env[encounter_action["res_model"]].browse(
            encounter_action["res_id"]
        )
        self.assertEqual(self.center, encounter.center_id)
        self.assertEqual(self.patient, encounter.patient_id)

    def test_create_encounter(self):
        encounter_action = self.env["medical.encounter"].create_encounter(
            patient=self.patient, center=self.center
        )
        encounter = self.env[encounter_action["res_model"]].browse(
            encounter_action["res_id"]
        )
        self.assertEqual(self.center, encounter.center_id)
        self.assertEqual(self.patient, encounter.patient_id)

    def test_create_encounter_create_patient(self):
        encounter_action = self.env["medical.encounter"].create_encounter(
            patient_vals={"name": "New patient"}, center=self.center
        )
        encounter = self.env[encounter_action["res_model"]].browse(
            encounter_action["res_id"]
        )
        self.assertEqual(self.center, encounter.center_id)
        self.assertNotEqual(self.patient, encounter.patient_id)
        self.assertEqual(encounter.patient_id.name, "New patient")

    def test_create_encounter_write_patient(self):
        encounter_action = self.env["medical.encounter"].create_encounter(
            patient_vals={"name": "New patient"},
            patient=self.patient,
            center=self.center,
        )
        encounter = self.env[encounter_action["res_model"]].browse(
            encounter_action["res_id"]
        )
        self.assertEqual(self.center, encounter.center_id)
        self.assertEqual(self.patient, encounter.patient_id)
        self.assertEqual(self.patient.name, "New patient")
