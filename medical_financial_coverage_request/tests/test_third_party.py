from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestThirdParty(TransactionCase):
    def setUp(self):
        super().setUp()
        self.type = self.browse_ref("medical_workflow.medical_workflow")
        self.activity = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity",
                "model_id": self.browse_ref(
                    "medical_clinical_request_group." "model_medical_request_group"
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

    def test_constrains_not_billable(self):
        vals = self.get_plan_values()
        vals["is_billable"] = False
        with self.assertRaises(ValidationError):
            self.env["workflow.plan.definition"].create(vals)

    def test_constrains_breakdown(self):
        vals = self.get_plan_values()
        vals["is_breakdown"] = True
        with self.assertRaises(ValidationError):
            self.env["workflow.plan.definition"].create(vals)

    def test_constrains_actions(self):
        vals = self.get_plan_values()
        vals["direct_action_ids"] = [
            (
                0,
                0,
                {"activity_definition_id": self.activity.id, "name": "Action"},
            ),
            (
                0,
                0,
                {
                    "activity_definition_id": self.activity.id,
                    "name": "Action2",
                },
            ),
        ]
        with self.assertRaises(ValidationError):
            self.env["workflow.plan.definition"].create(vals)

    def test_constrains_billable_action(self):
        vals = self.get_plan_values()
        vals["direct_action_ids"] = [
            (
                0,
                0,
                {
                    "activity_definition_id": self.activity.id,
                    "name": "Action",
                    "is_billable": True,
                },
            )
        ]
        with self.assertRaises(ValidationError):
            self.env["workflow.plan.definition"].create(vals)
