import datetime
from unittest.mock import patch

from odoo import sql_db
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestEncounterCreate(TransactionCase):
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
        with patch.object(
            sql_db.Cursor, "now", return_value=datetime.datetime(2023, 1, 1, 0, 0, 0)
        ):
            cls.patient = cls.env["medical.patient"].create({"name": "Demo Patient"})

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
        date = self.patient.write_date
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
        self.assertNotEqual(self.patient.write_date, date)

    def test_create_encounter_write_patient_unnecessary_fields(self):
        date = self.patient.write_date
        encounter_action = self.env["medical.encounter"].create_encounter(
            patient_vals={"display_name": False, "zip": ""},
            patient=self.patient,
            center=self.center,
        )
        encounter = self.env[encounter_action["res_model"]].browse(
            encounter_action["res_id"]
        )
        self.assertEqual(self.center, encounter.center_id)
        self.assertEqual(self.patient, encounter.patient_id)
        self.assertEqual(self.patient.write_date, date)

    def test_create_encounter_write_patient_assert(self):
        with patch.object(type(self.env["medical.patient"]), "write") as patient_write:
            self.env["medical.encounter"].create_encounter(
                patient_vals={"name": "New patient"},
                patient=self.patient,
                center=self.center,
            )
            patient_write.assert_called()

    def test_create_encounter_no_write_patient(self):
        with patch.object(type(self.env["medical.patient"]), "write") as patient_write:
            encounter_action = self.env["medical.encounter"].create_encounter(
                patient_vals={"name": self.patient.name},
                patient=self.patient,
                center=self.center,
            )
            patient_write.assert_not_called()
        encounter = self.env[encounter_action["res_model"]].browse(
            encounter_action["res_id"]
        )
        self.assertEqual(self.center, encounter.center_id)
        self.assertEqual(self.patient, encounter.patient_id)
