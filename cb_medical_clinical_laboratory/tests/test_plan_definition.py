# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPlanDefinition(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product = self.env["product.product"].create(
            {"type": "service", "name": "SERVICE"}
        )
        self.plan_definition = self.env["workflow.plan.definition"].create(
            {"name": "Plan", "is_billable": True}
        )
        self.plan_definition.activate()
        self.activity = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity",
                "service_id": self.product.id,
                "model_id": self.browse_ref(
                    "medical_clinical_laboratory." "model_medical_laboratory_request"
                ).id,
            }
        )
        self.activity2 = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity2",
                "service_id": self.product.id,
                "model_id": self.browse_ref(
                    "medical_clinical_procedure." "model_medical_procedure_request"
                ).id,
            }
        )
        self.activity.activate()
        self.lab_service = self.env["product.product"].create(
            {
                "default_code": "INTERNAL_CODE",
                "name": "name",
                "laboratory_request_ok": True,
                "type": "service",
            }
        )

    def test_onchange_action(self):
        action = self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": False,
                "name": "Action",
                "laboratory_service_ids": [(4, self.lab_service.id)],
            }
        )
        action.activity_definition_id = self.activity2
        action._onchange_activity_definition()
