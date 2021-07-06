from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestRecursion(TransactionCase):
    def setUp(self):
        super().setUp()
        self.type = self.browse_ref("medical_workflow.medical_workflow")
        self.activity = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity",
                "model_id": self.browse_ref(
                    "medical_clinical_request_group."
                    "model_medical_request_group"
                ).id,
                "type_id": self.type.id,
            }
        )

    def get_plan_values(self):
        return {
            "name": "Plan",
            "is_billable": True,
            "third_party_bill": True,
            "type_id": self.type.id,
            "is_breakdown": False,
            "direct_action_ids": [
                (
                    0,
                    0,
                    {
                        "activity_definition_id": self.activity.id,
                        "name": "Action",
                    },
                )
            ],
        }

    def test_recursion(self):
        vals = self.get_plan_values()
        plan = self.env["workflow.plan.definition"].create(vals)
        action_01 = self.env["workflow.plan.definition.action"].create(
            {
                "direct_plan_defintion_id": plan.id,
                "name": self.activity.name,
                "activity_definition_id": self.activity.id,
            }
        )
        action_02 = self.env["workflow.plan.definition.action"].create(
            {
                "direct_plan_defintion_id": plan.id,
                "name": self.activity.name,
                "activity_definition_id": self.activity.id,
                "trigger_action_ids": [(4, action_01.id)],
            }
        )
        self.assertEqual(action_01.triggerer_action_ids, action_02)
        with self.assertRaises(ValidationError):
            action_01.write({"trigger_action_ids": [(4, action_02.id)]})
