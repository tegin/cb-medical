from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMedicalQuote(TransactionCase):
    def setUp(self):
        super(TestMedicalQuote, self).setUp()
        self.medical_user_group = self.env.ref("medical_base.group_medical_reception")
        self.medical_user = self._create_user(
            "medical_user", self.medical_user_group.id
        )
        self.patient_model = self.env["medical.patient"]
        self.coverage_model = self.env["medical.coverage"]
        self.coverage_template_model = self.env["medical.coverage.template"]
        self.payor_model = self.env["res.partner"]
        self.coverage_agreement_model = self.env["medical.coverage.agreement"]
        self.coverage_agreement_model_item = self.env["medical.coverage.agreement.item"]
        self.center_model = self.env["res.partner"]
        self.product_model = self.env["product.product"]
        # self.type_model = self.env["workflow.type"]
        self.act_def_model = self.env["workflow.activity.definition"]
        self.action_model = self.env["workflow.plan.definition.action"]
        self.plan_model = self.env["workflow.plan.definition"]
        self.patient_1 = self._create_patient()
        self.patient_2 = self._create_patient()
        self.payor_1 = self._create_payor()
        self.coverage_template_1 = self._create_coverage_template()
        self.coverage = self._create_coverage(self.coverage_template_1)
        self.center_1 = self._create_center()
        self.product_1 = self._create_product("test 1")
        self.product_2 = self._create_product("test 2")
        # self.type_1 = self._create_type()
        self.act_def_1 = self._create_act_def()
        self.plan_1 = self._create_plan()
        self.action_1 = self._create_action()
        method_2 = self.browse_ref("cb_medical_careplan_sale.by_customer")
        auth_method = self.env["medical.authorization.method"].create(
            {
                "name": "Testing authorization_method",
                "code": "none",
                "invoice_group_method_id": method_2.id,
                "always_authorized": True,
            }
        )
        # case 1
        coverage_agreement_vals = {
            "name": "test coverage agreement",
            "center_ids": [(6, 0, [self.center_1.id])],
            "company_id": self.ref("base.main_company"),
            "authorization_method_id": auth_method.id,
            "authorization_format_id": self.browse_ref(
                "medical_financial_coverage_request.format_anything"
            ).id,
        }
        self.coverage_agreement = self.coverage_agreement_model.create(
            coverage_agreement_vals
        )
        self.item_1 = self.coverage_agreement_model_item.create(
            {
                "coverage_agreement_id": self.coverage_agreement.id,
                "plan_definition_id": self.plan_1.id,
                "product_id": self.product_1.id,
                "coverage_percentage": 40.0,
                "authorization_method_id": auth_method.id,
                "authorization_format_id": self.browse_ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
                "total_price": 200,
            }
        )

    def _create_user(self, name, group_ids):
        return (
            self.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": name,
                    "password": "demo",
                    "login": name,
                    "email": "@".join([name, "@test.com"]),
                    "groups_id": [(6, 0, [group_ids])],
                }
            )
        )

    def _create_patient(self):
        return self.patient_model.create({"name": "Test patient", "gender": "female"})

    def _create_payor(self):
        return self.payor_model.create(
            {
                "name": "Test payor",
                "is_payor": True,
                "email": "test.payor@test.com",
            }
        )

    def _create_coverage_template(self, state=False, payor=False):
        if not payor:
            payor = self.payor_1.id
        vals = {"name": "test coverage template", "payor_id": payor}
        if state:
            vals.update({"state": state})
        coverage_template = self.coverage_template_model.create(vals)
        return coverage_template

    def _create_coverage(self, coverage_template, state=False, patient=False):
        vals = {
            "name": "test coverage",
            "patient_id": self.patient_1.id,
            "coverage_template_id": coverage_template.id,
        }
        if state:
            vals.update({"state": state})
        if patient:
            vals.update({"patient_id": patient.id})
        coverage = self.coverage_model.create(vals)
        return coverage

    def _create_center(self):
        return self.center_model.create({"name": "Test location", "is_center": True})

    def _create_product(self, name):
        return self.product_model.create({"name": name, "type": "service"})

    def _create_act_def(self):
        return self.act_def_model.create(
            {
                "name": "Test activity",
                "service_id": self.product_1.id,
            }
        )

    def _create_action(self):
        return self.action_model.create(
            {
                "name": "Test action",
                "direct_plan_definition_id": self.plan_1.id,
                "activity_definition_id": self.act_def_1.id,
            }
        )

    def _create_plan(self):
        return self.plan_model.create(
            {
                "name": "Test plan",
            }
        )

    def test_onchange_medical_quote(self):
        comment_template = self.env["base.comment.template"].create(
            {"name": "Comment", "text": "Text"}
        )
        payor_2 = self._create_payor()
        coverage_template_2 = self._create_coverage_template(payor=payor_2.id)
        quote = self.env["medical.quote"].create(
            {
                "payor_id": self.payor_1.id,
                "is_private": True,
                "center_id": self.center_1.id,
                "coverage_template_id": self.coverage_template_1.id,
                "company_id": self.ref("base.main_company"),
            }
        )
        with Form(quote) as f:
            f.comment_template1_id = comment_template
            self.assertTrue(f.note1)

            f.comment_template2_id = comment_template
            self.assertTrue(f.note2)

            f.add_agreement_line_id = self.item_1
            self.assertEqual(f.add_quantity, 1)

            f.patient_id = self.patient_2
            self.assertFalse(f.coverage_template_id)

            f.payor_id = payor_2
            self.assertEqual(f.coverage_template_id, coverage_template_2)

    def test_quote_states(self):
        quote = self.env["medical.quote"].create(
            {
                "payor_id": self.payor_1.id,
                "is_private": True,
                "center_id": self.center_1.id,
                "coverage_template_id": self.coverage_template_1.id,
                "company_id": self.ref("base.main_company"),
            }
        )
        self.assertEqual(quote.state, "draft")
        quote.button_send()
        self.assertEqual(quote.state, "sent")
        quote.button_confirm()
        self.assertEqual(quote.state, "confirm")
        quote.button_cancel()
        self.assertEqual(quote.state, "cancel")
        quote.button_draft()
        self.assertEqual(quote.state, "draft")

    def test_medical_quote_private(self):
        quote = self.env["medical.quote"].create(
            {
                "payor_id": self.payor_1.id,
                "is_private": True,
                "center_id": self.center_1.id,
                "coverage_template_id": self.coverage_template_1.id,
                "company_id": self.ref("base.main_company"),
            }
        )
        quote.add_agreement_line_id = self.item_1.id
        quote.add_quantity = 2.0
        self.assertEqual(len(quote.quote_line_ids), 0)
        quote.button_add_line()
        self.assertEqual(len(quote.quote_line_ids), 1)
        line = quote.quote_line_ids
        self.assertEqual(line.coverage_agreement_id, self.coverage_agreement)
        self.assertEqual(line.plan_definition_id, self.plan_1)
        self.assertEqual(line.amount, 240)
        self.assertEqual(quote.amount, 240)

    def test_medical_quote_coverage(self):
        quote = self.env["medical.quote"].create(
            {
                "payor_id": self.payor_1.id,
                "is_private": False,
                "center_id": self.center_1.id,
                "coverage_template_id": self.coverage_template_1.id,
                "company_id": self.ref("base.main_company"),
            }
        )
        quote.add_agreement_line_id = self.item_1.id
        quote.add_quantity = 2.0
        self.assertEqual(len(quote.quote_line_ids), 0)
        quote.button_add_line()
        self.assertEqual(len(quote.quote_line_ids), 1)
        line = quote.quote_line_ids
        self.assertEqual(line.coverage_agreement_id, self.coverage_agreement)
        self.assertEqual(line.plan_definition_id, self.plan_1)
        self.assertEqual(line.amount, 160)
        self.assertEqual(quote.amount, 160)

        report_info = quote.lines_layouted()
        self.assertEqual(len(report_info[0][0]["lines"]), 1)

    def test_cuote_from_agreement(self):
        self.assertFalse(self.coverage_agreement.quote_ids)
        wizard = (
            self.env["wizard.create.quote.agreement"]
            .with_context(active_id=self.coverage_agreement.id)
            .create(
                {
                    "coverage_template_id": self.coverage_template_1.id,
                    "center_id": self.center_1.id,
                }
            )
        )
        wizard.generate_quote()
        self.assertTrue(self.coverage_agreement.quote_ids)

        self.assertEqual(len(self.coverage_agreement.quote_ids[0].quote_line_ids), 1)
        self.assertEqual(
            self.coverage_agreement.quote_ids[0].quote_line_ids[0].product_id,
            self.coverage_agreement.item_ids[0].product_id,
        )

    def test_send_email(self):
        quote = self.env["medical.quote"].create(
            {
                "payor_id": self.payor_1.id,
                "is_private": False,
                "center_id": self.center_1.id,
                "coverage_template_id": self.coverage_template_1.id,
                "company_id": self.ref("base.main_company"),
            }
        )
        action = quote.send_quote_by_email()
        email = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertEqual("mail.compose.message", email._name)
