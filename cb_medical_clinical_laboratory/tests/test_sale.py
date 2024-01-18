from odoo.exceptions import ValidationError
from odoo.tests.common import Form

from odoo.addons.cb_medical_pos.tests import common


class TestCBMedicalClinicalLaboratorySale(common.MedicalSavePointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.coverage_template.laboratory_code = "1"
        cls.coverage_template_2.laboratory_code = "2"
        cls.practitioner_01.write(
            {
                "agent": True,
                "commission_id": cls.env.ref("cb_medical_commission.commission_01").id,
            }
        )
        cls.practitioner_02.write(
            {
                "agent": True,
                "commission_id": cls.env.ref("cb_medical_commission.commission_01").id,
            }
        )
        cls.lab_service = cls.env["product.product"].create(
            {
                "default_code": "INTERNAL_CODE",
                "name": "name",
                "laboratory_request_ok": True,
                "type": "service",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.practitioner_01.id,
                            "product_code": "LAB_01",
                            "price": 5,
                        },
                    )
                ],
            }
        )
        cls.lab_service_2 = cls.env["product.product"].create(
            {
                "default_code": "INTERNAL_CODE2",
                "name": "name",
                "laboratory_request_ok": True,
                "type": "service",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.practitioner_01.id,
                            "product_code": "LAB_02",
                            "price": 5,
                        },
                    )
                ],
            }
        )
        cls.lab_service_agreement = cls.env["medical.coverage.agreement.item"].create(
            {
                "product_id": cls.lab_service.id,
                "coverage_agreement_id": cls.agreement.id,
                "total_price": 10.0,
                "coverage_percentage": 50.0,
                "authorization_method_id": cls.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": cls.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        cls.lab_service_2_agreement = cls.env["medical.coverage.agreement.item"].create(
            {
                "product_id": cls.lab_service_2.id,
                "coverage_agreement_id": cls.agreement.id,
                "total_price": 10.0,
                "coverage_percentage": 50.0,
                "authorization_method_id": cls.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": cls.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        cls.plan_definition.is_billable = True
        cls.plan_definition.is_breakdown = False
        cls.action4 = cls.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": cls.lab_activity.id,
                "direct_plan_definition_id": cls.plan_definition.id,
                "laboratory_service_ids": [(4, cls.lab_service.id)],
                "is_billable": False,
                "name": "Action4",
            }
        )

    def setUp(self):
        super().setUp()
        self.enc, self.careplan, self.group = self.create_careplan_and_group(
            self.agreement_line
        )

    def test_laboratory_views(self):
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        self.assertTrue(lab_req)
        event = self.enc.laboratory_sample_ids.generate_event(
            {
                "is_sellable_insurance": False,
                "is_sellable_private": False,
                "private_amount": 20,
                "laboratory_code": self.lab_service.default_code,
                "performer_id": self.practitioner_01.id,
                "coverage_amount": 10,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        with Form(event) as f:
            f.service_id = self.lab_service
        self.enc.refresh_laboratory_events()
        self.assertFalse(event.is_sellable_private)
        self.assertFalse(event.is_sellable_insurance)
        self.assertEqual(event.laboratory_code, "LAB_01")
        event.write(
            {
                "service_id": self.lab_service_2.id,
                "laboratory_code": self.lab_service_2.default_code,
            }
        )

    def test_laboratory_onchange_100_0(self):
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        sample = self.enc.laboratory_sample_ids
        event = sample.generate_event(
            {
                "service_id": self.lab_service.id,
                "performer_id": self.practitioner_01.id,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        self.lab_service_2_agreement.write(
            {
                "coverage_percentage": 100.0,
            }
        )
        event.write(
            {
                "service_id": self.lab_service_2.id,
            }
        )
        event.flush()
        self.assertFalse(event.is_sellable_private)
        self.assertTrue(event.is_sellable_insurance)
        self.assertEqual(event.coverage_amount, 10)
        self.assertEqual(event.private_amount, 0)
        self.assertEqual(event.coverage_cost, 5)
        self.assertEqual(event.private_cost, 0)

    def test_laboratory_onchange_50_50(self):
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        self.assertTrue(lab_req)
        sample = self.enc.laboratory_sample_ids
        event = sample.generate_event(
            {
                "service_id": self.lab_service.id,
                "performer_id": self.practitioner_01.id,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        self.lab_service_2_agreement.write(
            {
                "coverage_percentage": 50.0,
            }
        )
        event.write(
            {
                "service_id": self.lab_service_2.id,
            }
        )
        event.flush()
        self.assertTrue(event.is_sellable_private)
        self.assertTrue(event.is_sellable_insurance)
        self.assertEqual(event.coverage_amount, 5)
        self.assertEqual(event.private_amount, 5)
        self.assertEqual(event.coverage_cost, 2.5)
        self.assertEqual(event.private_cost, 2.5)

    def test_laboratory_onchange_0_100(self):
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        self.assertTrue(lab_req)
        sample = self.enc.laboratory_sample_ids
        event = sample.generate_event(
            {
                "service_id": self.lab_service.id,
                "performer_id": self.practitioner_01.id,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        self.assertFalse(lab_req.event_coverage_agreement_id)
        self.lab_service_2_agreement.write(
            {
                "coverage_percentage": 0.0,
            }
        )
        lab_req.refresh()
        event.write(
            {
                "service_id": self.lab_service_2.id,
            }
        )
        event.flush()
        self.assertTrue(event.is_sellable_private)
        self.assertFalse(event.is_sellable_insurance)
        self.assertEqual(event.coverage_amount, 0)
        self.assertEqual(event.private_amount, 10)
        self.assertEqual(event.coverage_cost, 0)
        self.assertEqual(event.private_cost, 5)

    def test_laboratory(self):
        self.assertTrue(self.group.laboratory_request_ids)
        action = self.group.with_context(
            model_name="medical.laboratory.request"
        ).action_view_request()
        self.assertEqual(
            self.group.laboratory_request_ids,
            self.env["medical.laboratory.request"].search(action["domain"]),
        )
        with self.assertRaises(ValidationError):
            self.env["wizard.medical.encounter.close"].create(
                {
                    "encounter_id": self.enc.id,
                    "pos_session_id": self.session.id,
                }
            ).run()
        for lab_req in self.group.laboratory_request_ids:
            self.assertEqual(lab_req.laboratory_event_count, 0)
            event = self.enc.laboratory_sample_ids.generate_event(
                {
                    "performer_id": self.practitioner_01.id,
                    "private_cost": 18,
                    "coverage_cost": 9,
                    "service_id": self.lab_service.id,
                }
            )
            self.assertEqual(
                event.id, lab_req.action_view_laboratory_events()["res_id"]
            )
            self.assertEqual(lab_req.laboratory_event_count, 1)
            sample = self.enc.laboratory_sample_ids
            sample.generate_event(
                {
                    "service_id": self.lab_service_2.id,
                    "performer_id": self.practitioner_01.id,
                    "private_cost": 18,
                    "coverage_cost": 9,
                }
            )
            self.assertEqual(lab_req.laboratory_event_count, 2)
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        sample = self.enc.laboratory_sample_ids
        event = sample.generate_event(
            {
                "service_id": self.lab_service.id,
                "performer_id": self.practitioner_01.id,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        event.service_id = self.lab_service
        event.flush()
        self.assertFalse(event.is_sellable_private)
        self.assertFalse(event.is_sellable_insurance)
        self.assertEqual(event.laboratory_code, "LAB_01")
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": self.enc.id, "pos_session_id": self.session.id}
        ).run()
        self.assertIn(self.enc.state, ["finished", "onleave"])
        self.assertTrue(
            self.enc.sale_order_ids.mapped("order_line").filtered(
                lambda r: r.medical_model == "medical.laboratory.event"
            )
        )
        self.enc.recompute_commissions()
        self.assertGreater(
            sum(
                a.amount
                for a in self.enc.sale_order_ids.mapped("order_line")
                .filtered(lambda r: r.medical_model == "medical.laboratory.event")
                .mapped("agent_ids")
            ),
            0,
        )

    def test_laboratory_check_code(self):
        self.assertTrue(self.group.laboratory_request_ids)
        action = self.group.with_context(
            model_name="medical.laboratory.request"
        ).action_view_request()
        self.assertEqual(
            self.group.laboratory_request_ids,
            self.env["medical.laboratory.request"].search(action["domain"]),
        )
        with self.assertRaises(ValidationError):
            self.env["wizard.medical.encounter.close"].create(
                {
                    "encounter_id": self.enc.id,
                    "pos_session_id": self.session.id,
                }
            ).run()
        for lab_req in self.group.laboratory_request_ids:
            self.assertEqual(lab_req.laboratory_event_count, 0)
            event = self.enc.laboratory_sample_ids.generate_event(
                {
                    "is_sellable_insurance": True,
                    "is_sellable_private": True,
                    "private_amount": 20,
                    "performer_id": self.practitioner_01.id,
                    "coverage_amount": 10,
                    "private_cost": 18,
                    "coverage_cost": 9,
                    "laboratory_code": "1234",
                }
            )
            self.assertFalse(lab_req.action_view_laboratory_events()["res_id"])
            self.assertEqual(
                event.id,
                self.enc.laboratory_sample_ids.action_view_laboratory_events()[
                    "res_id"
                ],
            )
            self.assertEqual(lab_req.laboratory_event_count, 0)
            self.assertEqual(self.enc.laboratory_sample_ids.laboratory_event_count, 1)
            self.enc.laboratory_sample_ids.generate_event(
                {
                    "is_sellable_insurance": False,
                    "is_sellable_private": False,
                    "private_amount": 20,
                    "laboratory_code": "12345",
                    "performer_id": self.practitioner_01.id,
                    "coverage_amount": 10,
                    "private_cost": 18,
                    "coverage_cost": 9,
                }
            )
            self.assertEqual(lab_req.laboratory_event_count, 0)
            self.assertEqual(self.enc.laboratory_sample_ids.laboratory_event_count, 2)
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)

        event = self.enc.laboratory_sample_ids.generate_event(
            {
                "is_sellable_insurance": False,
                "is_sellable_private": False,
                "private_amount": 20,
                "laboratory_code": self.lab_service.default_code,
                "performer_id": self.practitioner_01.id,
                "coverage_amount": 10,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        # We need to invoice the event, so we create an agreement item
        self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.product_07.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 0.0,
                "coverage_percentage": 50.0,
                "authorization_method_id": self.browse_ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        with Form(event) as form:
            form.service_id = self.lab_service_2
        self.assertEqual(event.name, self.lab_service_2.name)
        self.assertTrue(event.is_sellable_private)
        self.assertTrue(event.is_sellable_insurance)
        self.assertEqual(event.laboratory_code, "LAB_02")
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": self.enc.id, "pos_session_id": self.session.id}
        ).run()
        self.assertIn(self.enc.state, ["finished", "onleave"])
        order_lines = self.enc.sale_order_ids.mapped("order_line").filtered(
            lambda r: r.medical_model == "medical.laboratory.event"
            and r.medical_res_id == event.id
        )
        self.assertTrue(order_lines)
        for line in order_lines:
            self.assertEqual(line.name, self.lab_service_2.name)
        self.enc.recompute_commissions()
        self.assertGreater(
            sum(
                a.amount
                for a in self.enc.sale_order_ids.mapped("order_line")
                .filtered(lambda r: r.medical_model == "medical.laboratory.event")
                .mapped("agent_ids")
            ),
            0,
        )
