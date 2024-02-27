# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestMedicalQueue(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payor = cls.env["res.partner"].create(
            {"name": "Payor", "is_payor": True, "is_medical": True}
        )
        cls.coverage_template = cls.env["medical.coverage.template"].create(
            {"payor_id": cls.payor.id, "name": "Coverage"}
        )
        cls.company = cls.env.ref("base.main_company")
        cls.center = cls.env["res.partner"].create(
            {
                "name": "Center",
                "is_medical": True,
                "is_center": True,
                "encounter_sequence_prefix": "S",
                "stock_location_id": cls.env.ref("stock.warehouse0").id,
                "stock_picking_type_id": cls.env["stock.picking.type"]
                .search([], limit=1)
                .id,
            }
        )
        cls.performer = cls.env["res.partner"].create(
            {
                "name": "Performer",
                "is_medical": True,
                "is_practitioner": True,
            }
        )
        cls.performer_2 = cls.env["res.partner"].create(
            {
                "name": "Performer",
                "is_medical": True,
                "is_practitioner": True,
            }
        )
        cls.center_2 = cls.env["res.partner"].create(
            {
                "name": "Center2",
                "is_medical": True,
                "is_center": True,
                "encounter_sequence_prefix": "X",
                "stock_location_id": cls.env.ref("stock.warehouse0").id,
                "stock_picking_type_id": cls.env["stock.picking.type"]
                .search([], limit=1)
                .id,
            }
        )
        cls.location = cls.env["res.partner"].create(
            {
                "name": "Location",
                "is_medical": True,
                "is_location": True,
                "center_id": cls.center.id,
                "stock_location_id": cls.env.ref("stock.warehouse0").id,
                "stock_picking_type_id": cls.env["stock.picking.type"]
                .search([], limit=1)
                .id,
            }
        )
        cls.location_2 = cls.env["res.partner"].create(
            {
                "name": "Location 2",
                "is_medical": True,
                "is_location": True,
                "center_id": cls.center_2.id,
                "stock_location_id": cls.env.ref("stock.warehouse0").id,
                "stock_picking_type_id": cls.env["stock.picking.type"]
                .search([], limit=1)
                .id,
            }
        )
        cls.agreement = cls.env["medical.coverage.agreement"].create(
            {
                "name": "Agreement",
                "center_ids": [(4, cls.center.id), (4, cls.center_2.id)],
                "coverage_template_ids": [(4, cls.coverage_template.id)],
                "company_id": cls.company.id,
                "authorization_method_id": cls.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": cls.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        cls.patient_01 = cls.create_patient("Patient 01")
        cls.coverage_01 = cls.env["medical.coverage"].create(
            {
                "patient_id": cls.patient_01.id,
                "coverage_template_id": cls.coverage_template.id,
            }
        )
        cls.product_01 = cls.create_product("Medical resonance")
        cls.product_02 = cls.create_product("Report")
        cls.product_03 = cls.env["product.product"].create(
            {
                "type": "service",
                "name": "Clinical material",
                "is_medication": False,
                "lst_price": 10.0,
            }
        )

        cls.product_04 = cls.create_product("MR complex")
        cls.plan_definition = cls.env["workflow.plan.definition"].create(
            {"name": "Plan", "is_billable": True}
        )

        cls.plan_definition2 = cls.env["workflow.plan.definition"].create(
            {"name": "Plan2", "is_billable": True}
        )

        cls.activity = cls.env["workflow.activity.definition"].create(
            {
                "name": "Activity",
                "service_id": cls.product_02.id,
                "model_id": cls.env.ref(
                    "medical_clinical_procedure." "model_medical_procedure_request"
                ).id,
            }
        )
        cls.activity2 = cls.env["workflow.activity.definition"].create(
            {
                "name": "Activity2",
                "service_id": cls.product_03.id,
                "model_id": cls.env.ref(
                    "medical_clinical_procedure." "model_medical_procedure_request"
                ).id,
            }
        )
        cls.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": cls.activity.id,
                "direct_plan_definition_id": cls.plan_definition.id,
                "is_billable": False,
                "name": "Action",
            }
        )
        cls.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": cls.activity2.id,
                "direct_plan_definition_id": cls.plan_definition.id,
                "is_billable": False,
                "name": "Action2",
            }
        )
        cls.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": cls.activity.id,
                "direct_plan_definition_id": cls.plan_definition2.id,
                "is_billable": False,
                "name": "Action",
            }
        )
        cls.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": cls.activity2.id,
                "direct_plan_definition_id": cls.plan_definition2.id,
                "is_billable": False,
                "name": "Action2",
            }
        )
        cls.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": cls.activity2.id,
                "direct_plan_definition_id": cls.plan_definition2.id,
                "is_billable": False,
                "name": "Action3",
            }
        )
        cls.agreement_line = cls.env["medical.coverage.agreement.item"].create(
            {
                "product_id": cls.product_01.id,
                "coverage_agreement_id": cls.agreement.id,
                "plan_definition_id": cls.plan_definition.id,
                "total_price": 100,
                "authorization_method_id": cls.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": cls.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        cls.agreement_line2 = cls.env["medical.coverage.agreement.item"].create(
            {
                "product_id": cls.product_03.id,
                "coverage_agreement_id": cls.agreement.id,
                "plan_definition_id": cls.plan_definition.id,
                "total_price": 100.0,
                "authorization_method_id": cls.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": cls.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        cls.agreement_line3 = cls.env["medical.coverage.agreement.item"].create(
            {
                "product_id": cls.product_04.id,
                "coverage_agreement_id": cls.agreement.id,
                "plan_definition_id": cls.plan_definition2.id,
                "total_price": 100.0,
                "authorization_method_id": cls.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": cls.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        cls.queue_location = cls.env["queue.location"].create(
            {"name": "Queue Location"}
        )
        cls.queue_location_group = cls.env["queue.location.group"].create(
            {"name": "Queue Location Group"}
        )
        cls.queue_area = cls.env["queue.area"].create({"name": "Area"})

    @classmethod
    def create_patient(cls, name):
        return cls.env["medical.patient"].create({"name": name})

    @classmethod
    def create_product(cls, name):
        return cls.env["product.product"].create({"type": "service", "name": name})

    @classmethod
    def create_practitioner(cls, name):
        return cls.env["res.partner"].create(
            {"name": name, "is_practitioner": True, "agent": True}
        )

    def create_careplan_and_group(self, line=None, extra_vals=None):
        if line is None:
            line = self.agreement_line
        if extra_vals is None:
            extra_vals = {}
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        careplan = self.env["medical.careplan"].create(
            {
                "patient_id": encounter.patient_id.id,
                "encounter_id": encounter.id,
                "center_id": encounter.center_id.id,
                "coverage_id": self.coverage_01.id,
            }
        )
        wizard_vals = {
            "careplan_id": careplan.id,
            "agreement_line_id": line.id,
        }
        wizard_vals.update(extra_vals)
        wizard = self.env["medical.careplan.add.plan.definition"].create(wizard_vals)
        wizard.run()
        group = self.env["medical.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        group.ensure_one()
        self.assertEqual(group.center_id, encounter.center_id)
        return encounter, careplan, group

    def test_no_queue_token(self):
        encounter, careplan, group = self.create_careplan_and_group()
        self.assertFalse(encounter.queue_token_id)
        self.assertFalse(group.queue_token_location_id)

    def test_queue_token_area_no_matching(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "area",
                "queue_area_id": self.queue_area.id,
            }
        )
        self.env["queue.location.area"].create(
            {
                "area_id": self.queue_area.id,
                "center_id": self.center_2.id,
                "location_id": self.queue_location.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group()
        self.assertFalse(encounter.queue_token_id)
        self.assertFalse(group.queue_token_location_id)

    def test_queue_token_area_location_matching(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "area",
                "queue_area_id": self.queue_area.id,
            }
        )

        self.env["queue.location.area"].create(
            {
                "area_id": self.queue_area.id,
                "center_id": self.center.id,
                "location_id": self.queue_location.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group()
        self.assertTrue(encounter.queue_token_id)
        self.assertTrue(group.queue_token_location_id)
        # Testing some stuff of views here
        self.assertTrue(encounter.queue_token_id.encounter_count, 1)
        action = encounter.queue_token_id.view_encounter()
        self.assertEqual(
            encounter, self.env[action["res_model"]].browse(action["res_id"])
        )
        self.assertTrue(group.queue_token_location_id.request_group_count, 1)
        action = group.queue_token_location_id.view_encounter()
        self.assertEqual(
            encounter, self.env[action["res_model"]].browse(action["res_id"])
        )

    def test_queue_token_area_group_matching(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "area",
                "queue_area_id": self.queue_area.id,
            }
        )
        self.env["queue.location.area"].create(
            {
                "area_id": self.queue_area.id,
                "center_id": self.center.id,
                "group_id": self.queue_location_group.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group()
        self.assertTrue(encounter.queue_token_id)
        self.assertTrue(group.queue_token_location_id)

    def test_queue_token_area_error_matching(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "area",
                "queue_area_id": self.queue_area.id,
            }
        )
        self.env["queue.location.area"].create(
            {
                "area_id": self.queue_area.id,
                "center_id": self.center.id,
                "location_id": self.queue_location.id,
                "group_id": self.queue_location_group.id,
            }
        )
        with self.assertRaises(ValidationError):
            encounter, careplan, group = self.create_careplan_and_group()

    def test_queue_token_area_misconfigured_matching(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "area",
                "queue_area_id": self.queue_area.id,
            }
        )
        self.env["queue.location.area"].create(
            {
                "area_id": self.queue_area.id,
                "center_id": self.center.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group()
        self.assertFalse(encounter.queue_token_id)
        self.assertFalse(group.queue_token_location_id)

    def test_queue_token_cancelling(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "area",
                "queue_area_id": self.queue_area.id,
            }
        )
        self.env["queue.location.area"].create(
            {
                "area_id": self.queue_area.id,
                "center_id": self.center.id,
                "group_id": self.queue_location_group.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group()
        self.assertTrue(encounter.queue_token_id)
        self.assertTrue(group.queue_token_location_id)
        self.assertEqual(group.queue_token_location_id.state, "draft")
        token_location = group.queue_token_location_id
        group.cancel()
        self.assertFalse(group.queue_token_location_id)
        token_location.refresh()
        self.assertEqual(token_location.state, "cancelled")

    def test_queue_token_performer_location_matching(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "performer",
                "performer_required": True,
            }
        )
        self.env["res.partner.queue.location"].create(
            {
                "practitioner_id": self.performer.id,
                "center_id": self.center.id,
                "location_id": self.queue_location.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group(
            extra_vals={
                "performer_id": self.performer.id,
            }
        )
        self.assertTrue(encounter.queue_token_id)
        self.assertTrue(group.queue_token_location_id)

    def test_queue_token_performer_location_matching_dont_send(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "performer",
                "performer_required": True,
            }
        )
        self.env["res.partner.queue.location"].create(
            {
                "practitioner_id": self.performer.id,
                "center_id": self.center.id,
                "location_id": self.queue_location.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group(
            extra_vals={"performer_id": self.performer.id, "send_to_queue": False}
        )
        self.assertFalse(encounter.queue_token_id)

    def test_queue_token_change_performer_different_location(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "performer",
                "performer_required": True,
            }
        )
        self.env["res.partner.queue.location"].create(
            {
                "practitioner_id": self.performer.id,
                "center_id": self.center.id,
                "location_id": self.queue_location.id,
            }
        )
        self.env["res.partner.queue.location"].create(
            {
                "practitioner_id": self.performer_2.id,
                "center_id": self.center.id,
                "group_id": self.queue_location_group.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group(
            extra_vals={
                "performer_id": self.performer.id,
            }
        )
        self.assertTrue(encounter.queue_token_id)
        self.assertTrue(group.queue_token_location_id)
        self.assertEqual(group.queue_token_location_id.location_id, self.queue_location)
        self.assertFalse(group.queue_token_location_id.group_id)
        group.performer_id = self.performer_2
        self.assertFalse(group.queue_token_location_id.location_id)
        self.assertEqual(
            group.queue_token_location_id.group_id, self.queue_location_group
        )

    def test_queue_token_change_performer_cancel(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "performer",
                "performer_required": True,
            }
        )
        self.env["res.partner.queue.location"].create(
            {
                "practitioner_id": self.performer.id,
                "center_id": self.center.id,
                "location_id": self.queue_location.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group(
            extra_vals={
                "performer_id": self.performer.id,
            }
        )
        self.assertTrue(encounter.queue_token_id)
        self.assertTrue(group.queue_token_location_id)
        self.assertEqual(group.queue_token_location_id.location_id, self.queue_location)
        self.assertFalse(group.queue_token_location_id.group_id)
        queue_token_location = group.queue_token_location_id
        group.performer_id = self.performer_2
        self.assertFalse(group.queue_token_location_id)
        self.assertEqual(queue_token_location.state, "cancelled")

    def test_queue_token_performer_all_center(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "performer",
                "performer_required": True,
            }
        )
        self.env["res.partner.queue.location"].create(
            {
                "practitioner_id": self.performer.id,
                "location_id": self.queue_location.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group(
            extra_vals={
                "performer_id": self.performer.id,
            }
        )
        self.assertTrue(encounter.queue_token_id)
        self.assertTrue(group.queue_token_location_id)
        self.assertEqual(group.queue_token_location_id.location_id, self.queue_location)
        self.assertFalse(group.queue_token_location_id.group_id)

    def test_queue_token_performer_group_matching(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "performer",
                "performer_required": True,
            }
        )
        self.env["res.partner.queue.location"].create(
            {
                "practitioner_id": self.performer.id,
                "center_id": self.center.id,
                "group_id": self.queue_location_group.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group(
            extra_vals={
                "performer_id": self.performer.id,
            }
        )
        self.assertTrue(encounter.queue_token_id)
        self.assertTrue(group.queue_token_location_id)

    def test_queue_token_performer_misconfigured_matching(self):
        self.plan_definition.write(
            {
                "generate_queue_task": "performer",
                "performer_required": True,
            }
        )
        self.env["res.partner.queue.location"].create(
            {
                "practitioner_id": self.performer.id,
                "center_id": self.center.id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group(
            extra_vals={
                "performer_id": self.performer.id,
            }
        )
        self.assertFalse(encounter.queue_token_id)
        self.assertFalse(group.queue_token_location_id)
