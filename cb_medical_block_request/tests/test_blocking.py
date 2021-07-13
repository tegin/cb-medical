from odoo.addons.cb_medical_pos.tests import common
from odoo.exceptions import ValidationError


class TestCBMedicalCommission(common.MedicalSavePointCase):
    def test_blocking_failure(self):
        self.plan_definition2.action_ids.write({"is_blocking": True})
        self.plan_definition2.write({"third_party_bill": False})
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(len(group.procedure_request_ids), 1)
        self.assertTrue(group.procedure_request_ids.is_blocking)
        self.assertTrue(group.procedure_request_ids.is_blocking)
        with self.assertRaises(ValidationError):
            self.env["wizard.medical.encounter.close"].create(
                {
                    "encounter_id": encounter.id,
                    "pos_session_id": self.session.id,
                }
            ).run()

    def test_blocking_ok(self):
        self.plan_definition2.action_ids.write({"is_blocking": True})
        self.plan_definition2.write({"third_party_bill": False})
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(len(group.procedure_request_ids), 1)
        self.assertTrue(group.procedure_request_ids.is_blocking)
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.state, "active")
            request.active2completed()
            self.assertEqual(request.state, "completed")
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertIn(encounter.state, ["onleave", "finished"])

    def test_unblocking(self):
        self.plan_definition2.write({"third_party_bill": False})
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(len(group.procedure_request_ids), 1)
        self.assertFalse(group.procedure_request_ids.is_blocking)
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertIn(encounter.state, ["onleave", "finished"])
