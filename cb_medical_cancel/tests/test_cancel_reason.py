from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCancelReason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["medical.patient"].create({"name": "Patient"})
        cls.center = cls.env["res.partner"].create(
            {
                "name": "center",
                "is_center": True,
                "is_medical": True,
                "encounter_sequence_prefix": "C",
            }
        )
        cls.encounter = cls.env["medical.encounter"].create(
            {
                "name": "Test Encounter",
                "patient_id": cls.patient.id,
                "center_id": cls.center.id,
            }
        )
        cls.careplan = cls.env["medical.careplan"].create(
            {
                "patient_id": cls.patient.id,
                "center_id": cls.center.id,
                "encounter_id": cls.encounter.id,
            }
        )
        cls.reason = cls.env["medical.cancel.reason"].create(
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
        self.careplan.invalidate_recordset()
        self.assertEqual(self.careplan.fhir_state, "cancelled")

    def test_cancel_document(self):
        document = self.env["medical.document.reference"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.careplan.encounter_id.id,
                "careplan_id": self.careplan.id,
                "center_id": self.center.id,
                "parent_id": self.careplan.id,
                "parent_model": self.careplan._name,
                "document_type_id": self.env["medical.document.type"]
                .create({"name": "Test Document Type"})
                .id,
                "text": "Test document",
            }
        )
        self.assertTrue(document.encounter_id)
        self.env["medical.careplan.cancel"].create(
            {
                "request_id": self.careplan.id,
                "cancel_reason_id": self.reason.id,
                "cancel_reason": "testing purposes",
            }
        ).run()
        self.careplan.invalidate_recordset()
        self.assertEqual(self.careplan.fhir_state, "cancelled")
        self.assertNotEqual(document.fhir_state, "cancelled")
        self.assertFalse(document.parent_id)
        self.assertEqual(document.encounter_id, self.encounter)

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
        laboratory_request.flush_recordset()
        self.careplan.encounter_id = encounter.id
        self.careplan.invalidate_recordset()
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
        wizard.flush_recordset()
        wizard.run()
        encounter.invalidate_recordset()
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
