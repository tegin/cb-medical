# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.cb_test.tests.test_cb import TestCB


class TestCBPractitioner(TestCB):
    def test_practitioner_conditions(self):
        self.plan_definition2.write({"third_party_bill": False})
        self.plan_definition2.action_ids.write(
            {"variable_fee": 0, "fixed_fee": 10}
        )
        self.assertNotEqual(
            self.plan_definition2.action_ids.activity_definition_id.service_id,
            self.agreement_line3.product_id,
        )
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env["medical.practitioner.condition"].create(
            {
                "practitioner_id": self.practitioner_02.id,
                "variable_fee": 10,
                "fixed_fee": 0,
                "procedure_service_id": self.agreement_line3.product_id.id,
            }
        )
        self.assertEqual(self.agreement_line3.product_id, group.service_id)
        for request in group.procedure_request_ids:
            request.draft2active()
            procedure = request.generate_event()
            self.assertEqual(request.state, "active")
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            procedure._onchange_check_condition()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02
            )
            self.assertFalse(procedure.practitioner_condition_id)
            self.assertEqual(request.variable_fee, 0)
            self.assertEqual(request.fixed_fee, 10)
            general_cond = self.env["medical.practitioner.condition"].create(
                {
                    "practitioner_id": self.practitioner_02.id,
                    "variable_fee": 10,
                    "fixed_fee": 0,
                }
            )
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, general_cond)
            self.assertEqual(procedure.variable_fee, 10)
            self.assertEqual(procedure.fixed_fee, 0)
            proc_cond = self.env["medical.practitioner.condition"].create(
                {
                    "practitioner_id": self.practitioner_02.id,
                    "variable_fee": 0,
                    "fixed_fee": 5,
                    "procedure_service_id": self.product_02.id,
                }
            )
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, proc_cond)
            self.assertEqual(procedure.variable_fee, 0)
            self.assertEqual(procedure.fixed_fee, 5)
            group_cond = self.env["medical.practitioner.condition"].create(
                {
                    "practitioner_id": self.practitioner_02.id,
                    "variable_fee": 0,
                    "fixed_fee": 15,
                    "service_id": self.product_04.id,
                }
            )
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, group_cond)
            self.assertEqual(procedure.variable_fee, 0)
            self.assertEqual(procedure.fixed_fee, 15)
            cond = self.env["medical.practitioner.condition"].create(
                {
                    "practitioner_id": self.practitioner_02.id,
                    "variable_fee": 0,
                    "fixed_fee": 0,
                    "service_id": self.product_04.id,
                    "procedure_service_id": self.product_02.id,
                }
            )
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, cond)
            self.assertEqual(procedure.variable_fee, 0)
            self.assertEqual(procedure.fixed_fee, 0)
