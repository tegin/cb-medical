from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestCancelReason(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.center = self.env["res.partner"].create(
            {"name": "center", "is_center": True, "is_medical": True}
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
            self.careplan.write({"state": "cancelled"})

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
        self.assertEqual(self.careplan.state, "cancelled")
