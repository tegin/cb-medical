from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCancelReason(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.center = self.env["res.partner"].create(
            {
                "name": "center",
                "is_center": True,
                "is_medical": True,
                "encounter_sequence_prefix": "C",
            }
        )
        self.careplan = self.env["medical.careplan"].create(
            {"patient_id": self.patient.id, "center_id": self.center.id}
        )
        self.reason = self.env["medical.cancel.reason"].create(
            {"name": "Cancel reason", "description": "Cancel reason"}
        )

    def test_constrains_01(self):
        with self.assertRaises(ValidationError):
            self.careplan.write({"cancel_reason_id": self.reason.id})

    def test_constrains_02(self):
        with self.assertRaises(ValidationError):
            self.careplan.write({"fhir_state": "cancelled"})

    def test_cancel_process_failure(self):
        with self.assertRaises(ValidationError):
            self.careplan.cancel()

    def test_cancel_careplan(self):
        self.env["medical.careplan.cancel"].create(
            {
                "request_id": self.careplan.id,
                "cancel_reason_id": self.reason.id,
                "cancel_reason": "testing purposes",
            }
        ).run()
        self.careplan.refresh()
        self.assertEqual(self.careplan.fhir_state, "cancelled")

    def test_cancel_encounter(self):
        encounter = self.env["medical.encounter"].create(
            {
                "name": "Test Encounter",
                "patient_id": self.patient.id,
                "center_id": self.center.id,
            }
        )
        laboratory_request = self.env["medical.laboratory.request"].create(
            {
                "patient_id": self.patient.id,
                "careplan_id": self.careplan.id,
                "center_id": self.center.id,
                "encounter_id": encounter.id,
            }
        )
        laboratory_request.flush()
        self.careplan.encounter_id = encounter.id
        self.assertEqual(self.careplan.fhir_state, "draft")
        self.pos_config = self.env["pos.config"].create({"name": "PoS config"})
        session = self.env["pos.session"].create(
            {"config_id": self.pos_config.id, "user_id": self.env.uid}
        )
        wizard = self.env["medical.encounter.cancel"].create(
            {
                "encounter_id": encounter.id,
                "cancel_reason_id": self.reason.id,
                "cancel_reason": "Test cancel reason",
                "pos_session_id": session.id,
            }
        )
        wizard.flush()
        wizard.run()
        encounter.refresh()
        self.assertEqual(encounter.state, "finished")
        self.assertTrue(encounter.cancel_reason_id)
        self.assertEqual(encounter.cancel_reason_id, self.reason)
        self.assertEqual(self.careplan.fhir_state, "cancelled")
        self.assertEqual(self.careplan.laboratory_request_ids.fhir_state, "cancelled")
        with self.assertRaises(ValidationError):
            encounter.state = "cancelled"
            encounter.cancel(self.reason, session, "Cancel reason")
        self.careplan.reactive()
        self.assertEqual(self.careplan.fhir_state, "active")
        self.assertFalse(self.careplan.cancel_reason_id)
