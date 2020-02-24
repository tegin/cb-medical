# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.cb_test.tests.test_cb import TestCB
from odoo.exceptions import ValidationError
from odoo.tests.common import at_install, post_install


@post_install(True)
@at_install(False)
class TestCBTrigger(TestCB):
    def test_trigger(self):
        self.plan_definition.is_billable = True
        self.plan_definition.is_breakdown = False
        self.action2.write({"trigger_action_ids": [(4, self.action.id)]})
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(
            group.procedure_request_ids.filtered(lambda r: r.trigger_ids)
        )
        self.assertTrue(
            group.medication_request_ids.filtered(lambda r: r.triggerer_ids)
        )

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
            procedure = request.generate_event()
            self.assertEqual(request.state, "active")
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02
            )
            procedure.preparation2in_progress()
            procedure.in_progress2completed()
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
