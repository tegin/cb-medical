from odoo.exceptions import UserError, ValidationError

from ..tests import common


class TestCBMedicalCommission(common.MedicalSavePointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reina = cls.env["res.partner"].create(
            {
                "name": "Reina",
                "is_medical": True,
                "is_center": True,
                "encounter_sequence_prefix": "9",
            }
        )
        cls.def_third_party_product = cls.create_product("THIRD PARTY PRODUCT")
        cls.env["ir.config_parameter"].set_param(
            "cb.default_third_party_product", cls.def_third_party_product.id
        )

    def test_session_sequence(self):
        self.assertNotRegex(self.session.internal_identifier, r"^MYSEQ.*$")
        self.session.action_pos_session_approve()
        self.pos_config.write({"session_sequence_prefix": "MYSEQ"})
        self.pos_config.flush()
        self.pos_config.open_session_cb()
        session = self.pos_config.current_session_id
        self.assertNotEqual(session, self.session)
        self.assertRegex(session.internal_identifier, r"^MYSEQ.*$")

    def test_careplan_sale_multicompany(self):
        """
        We will create several encounters with two payments, one
        for one company and one for the other
        We will review that the expected moves are created at the end.
        """
        self.create_inter_company(self.company, self.company_2)
        encounters = self.env["medical.encounter"]
        for _i in range(0, 10):
            encounter = self.env["medical.encounter"].create(
                {"patient_id": self.patient_01.id, "center_id": self.center.id}
            )
            careplan = self.env["medical.careplan"].new(
                {
                    "patient_id": self.patient_01.id,
                    "encounter_id": encounter.id,
                    "coverage_id": self.coverage_01.id,
                    "sub_payor_id": self.sub_payor.id,
                }
            )
            careplan._onchange_encounter()
            careplan = careplan.create(careplan._convert_to_write(careplan._cache))
            self.assertEqual(careplan.center_id, encounter.center_id)
            order = (
                self.env["wizard.medical.encounter.add.amount"]
                .create(
                    {
                        "encounter_id": encounter.id,
                        "amount": 10,
                        "payment_method_id": self.payment_method_id.id,
                        "pos_session_id": self.session.id,
                    }
                )
                ._run()
            )
            self.assertFalse(order.lines)
            self.assertTrue(order.payment_ids)
            wizard = self.env["medical.careplan.add.plan.definition"].create(
                {
                    "careplan_id": careplan.id,
                    "agreement_line_id": self.agreement_line.id,
                }
            )
            self.action.is_billable = False
            wizard.run()
            groups = self.env["medical.request.group"].search(
                [("careplan_id", "=", careplan.id)]
            )
            self.assertTrue(groups)
            action = encounter.medical_encounter_close_action()
            self.env[action["res_model"]].with_context(**action["context"]).create(
                {"pos_session_id": self.session.id}
            ).run()
            self.assertTrue(encounter.sale_order_ids)
            self.assertGreater(self.session.encounter_count, 0)
            self.assertGreater(self.session.sale_order_count, 0)
            self.assertEqual(
                self.session.action_view_encounters()["res_id"], encounter.id
            )
            self.assertGreater(encounter.pending_private_amount, 0)
            self.env["wizard.medical.encounter.finish"].create(
                {
                    "encounter_id": encounter.id,
                    "pos_session_id": self.session_2.id,
                    "payment_method_id": self.payment_method_2.id,
                }
            ).run()
            self.assertEqual(encounter.pending_private_amount, 0)
            encounters |= encounter
        self.session.action_pos_session_closing_control()
        self.session.action_pos_session_approve()
        for encounter in encounters:
            encounter.reconcile_payments()
            self.assertFalse(encounter.reconcile_move_id)

        self.session_2.action_pos_session_closing_control()
        self.session_2.action_pos_session_approve()
        for encounter in encounters:
            encounter.reconcile_payments()
            self.assertTrue(encounter.reconcile_move_id)
            invoices = encounter.sale_order_ids.invoice_ids
            for invoice in invoices:
                self.assertEqual(0, invoice.amount_residual)

    def test_careplan_no_amount(self):
        """
        We want to check that an error is raised when no inter-company configuration is made
        """
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        with self.assertRaises(ValidationError):
            self.env["wizard.medical.encounter.add.amount"].create(
                {
                    "encounter_id": encounter.id,
                    "amount": 0,
                    "payment_method_id": self.payment_method_id.id,
                    "pos_session_id": self.session.id,
                }
            )._run()

    def test_careplan_sale_multicompany_not_configured(self):
        """
        We want to check that an error is raised when no inter-company configuration is made
        """
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        careplan = self.env["medical.careplan"].new(
            {
                "patient_id": self.patient_01.id,
                "encounter_id": encounter.id,
                "coverage_id": self.coverage_01.id,
                "sub_payor_id": self.sub_payor.id,
            }
        )
        careplan._onchange_encounter()
        careplan = careplan.create(careplan._convert_to_write(careplan._cache))
        self.assertEqual(careplan.center_id, encounter.center_id)
        order = (
            self.env["wizard.medical.encounter.add.amount"]
            .create(
                {
                    "encounter_id": encounter.id,
                    "amount": 10,
                    "payment_method_id": self.payment_method_id.id,
                    "pos_session_id": self.session.id,
                }
            )
            ._run()
        )
        self.assertFalse(order.lines)
        self.assertTrue(order.payment_ids)
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line.id,
            }
        )
        self.action.is_billable = False
        wizard.run()
        groups = self.env["medical.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertTrue(groups)
        action = encounter.medical_encounter_close_action()
        self.env[action["res_model"]].with_context(**action["context"]).create(
            {"pos_session_id": self.session.id}
        ).run()
        self.assertTrue(encounter.sale_order_ids)
        self.assertGreater(self.session.encounter_count, 0)
        self.assertGreater(self.session.sale_order_count, 0)
        self.assertEqual(self.session.action_view_encounters()["res_id"], encounter.id)
        self.assertGreater(encounter.pending_private_amount, 0)
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session_2.id,
                "payment_method_id": self.payment_method_2.id,
            }
        ).run()
        self.assertEqual(encounter.pending_private_amount, 0)
        self.session.action_pos_session_closing_control()
        self.session.action_pos_session_approve()
        encounter.reconcile_payments()
        self.assertFalse(encounter.reconcile_move_id)

        self.session_2.action_pos_session_closing_control()
        self.session_2.action_pos_session_approve()
        with self.assertRaises(UserError):
            encounter.reconcile_payments()

    def test_careplan_sale(self):
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        careplan = self.env["medical.careplan"].new(
            {
                "patient_id": self.patient_01.id,
                "encounter_id": encounter.id,
                "coverage_id": self.coverage_01.id,
                "sub_payor_id": self.sub_payor.id,
            }
        )
        careplan._onchange_encounter()
        careplan = careplan.create(careplan._convert_to_write(careplan._cache))
        self.assertEqual(careplan.center_id, encounter.center_id)
        order = (
            self.env["wizard.medical.encounter.add.amount"]
            .create(
                {
                    "encounter_id": encounter.id,
                    "amount": 10,
                    "payment_method_id": self.payment_method_id.id,
                    "pos_session_id": self.session.id,
                }
            )
            ._run()
        )
        self.assertFalse(order.lines)
        self.assertTrue(order.payment_ids)
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line.id,
            }
        )
        self.action.is_billable = False
        wizard.run()
        groups = self.env["medical.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertTrue(groups)
        action = encounter.medical_encounter_close_action()
        self.env[action["res_model"]].with_context(**action["context"]).create(
            {"pos_session_id": self.session.id}
        ).run()
        self.assertTrue(encounter.sale_order_ids)
        self.assertGreater(self.session.encounter_count, 0)
        self.assertGreater(self.session.sale_order_count, 0)
        self.assertEqual(self.session.action_view_encounters()["res_id"], encounter.id)
        self.assertGreater(encounter.pending_private_amount, 0)
        lines = len(
            self.env["pos.payment"].search([("session_id", "=", self.session.id)])
        )
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "payment_method_id": self.payment_method_id.id,
            }
        ).run()
        self.assertFalse(encounter.sale_order_ids.filtered(lambda r: r.is_down_payment))
        invoice = encounter.sale_order_ids.filtered(
            lambda r: not r.coverage_agreement_id and not r.is_down_payment
        ).mapped("invoice_ids")
        for line in invoice.invoice_line_ids:
            self.assertNotEqual(line.name, "/")
        self.assertGreater(
            len(self.env["pos.payment"].search([("session_id", "=", self.session.id)])),
            lines,
        )
        self.assertEqual(encounter.pending_private_amount, 0)
        self.session.action_pos_session_closing_control()
        # self.assertTrue(self.session.sale_order_line_ids)
        # self.assertTrue(self.session.request_group_ids)
        # self.assertTrue(self.session.down_payment_ids)
        self.session.action_pos_session_approve()
        encounter.reconcile_payments()
        invoices = encounter.sale_order_ids.invoice_ids
        self.assertTrue(invoices)
        invoices.invalidate_cache()
        invoices.refresh()
        for invoice in invoices:
            self.assertEqual(0, invoice.amount_residual)

    def test_performer(self):
        self.plan_definition2.write(
            {"third_party_bill": False, "performer_required": True}
        )
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity5.id,
                "direct_plan_definition_id": self.plan_definition2.id,
                "is_billable": False,
                "name": "Action",
                "performer_id": self.practitioner_02.id,
            }
        )
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        careplan_wizard = (
            self.env["medical.encounter.add.careplan"]
            .with_context(default_encounter_id=encounter.id)
            .new({"coverage_id": self.coverage_01.id})
        )
        careplan_wizard.onchange_coverage()
        careplan_wizard.onchange_coverage_template()
        careplan_wizard.onchange_payor()
        careplan_wizard = careplan_wizard.create(
            careplan_wizard._convert_to_write(careplan_wizard._cache)
        )
        self.assertEqual(encounter, careplan_wizard.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard.center_id)
        careplan_wizard.run()
        careplan = encounter.careplan_ids
        self.assertEqual(careplan.center_id, encounter.center_id)
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line3.id,
                "performer_id": self.practitioner_01.id,
            }
        )
        self.assertIn(self.agreement, wizard.agreement_ids)
        self.action.is_billable = False
        wizard.run()
        group = self.env["medical.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        group.ensure_one()
        self.assertEqual(group.center_id, encounter.center_id)
        self.assertEqual(group.performer_id, self.practitioner_01)
        group.refresh()
        self.assertEqual(len(group.procedure_request_ids.ids), 2)
        self.assertTrue(
            group.procedure_request_ids.filtered(
                lambda r: r.performer_id == self.practitioner_01
            )
        )
        self.assertTrue(
            group.procedure_request_ids.filtered(
                lambda r: r.performer_id == self.practitioner_02
            )
        )

    def test_down_payments_third_party(self):
        self.plan_definition2.third_party_bill = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env["wizard.medical.encounter.add.amount"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "payment_method_id": self.payment_method_id.id,
                "amount": 100,
            }
        ).run()
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_02
        self.practitioner_02.third_party_sequence_id = self.env["ir.sequence"].create(
            {"name": "sequence"}
        )
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertEqual(encounter.pending_private_amount, 0)
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "payment_method_id": self.payment_method_id.id,
            }
        ).run()
        sale_order = encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment and not r.third_party_partner_id
        )
        self.assertTrue(sale_order)
        self.assertEqual(sum(s.amount_total for s in sale_order), 0)
        payments = self.env["pos.payment"].search(
            [("session_id", "=", self.session.id)]
        )
        sale_order = encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment and r.third_party_partner_id
        )
        self.assertTrue(sale_order)
        self.assertEqual(100, sum(p.amount for p in payments))
        self.assertEqual(sum(s.amount_total for s in sale_order), 100)
        self.session.action_pos_session_approve()
        encounter.reconcile_payments()
        self.assertFalse(encounter.sale_order_ids.invoice_ids)
        move_lines = encounter.mapped("pos_payment_ids.pos_order_id.deposit_line_id")
        self.assertTrue(move_lines)
        for move_line in move_lines:
            self.assertEqual(0, move_line.amount_residual)

    def test_third_party(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(encounter.sale_order_count, 0)
        self.assertTrue(group.procedure_request_ids)
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_02
        self.practitioner_02.third_party_sequence_id = self.env["ir.sequence"].create(
            {"name": "sequence"}
        )
        self.assertTrue(group.is_sellable_insurance or group.is_sellable_private)
        self.assertTrue(group.third_party_bill)
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertGreater(encounter.sale_order_count, 0)
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertTrue(sale_order.third_party_order)
        self.assertEqual(sale_order.third_party_partner_id, self.practitioner_02)
        self.assertGreater(encounter.pending_private_amount, 0)
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "payment_method_id": self.payment_method_id.id,
            }
        ).run()
        self.assertFalse(sale_order.invoice_ids)
        self.assertEqual(encounter.pending_private_amount, 0)
        self.session.action_pos_session_approve()
        encounter.reconcile_payments()
        invoices = encounter.sale_order_ids.invoice_ids
        self.assertFalse(invoices)
        moves = encounter.sale_order_ids.third_party_move_id
        self.assertTrue(moves)
        line = moves.line_ids.filtered(
            lambda r: r.partner_id == self.patient_01.partner_id
        )
        self.assertTrue(line)
        self.assertEqual(line.amount_residual, 0)
        payments = self.env["pos.payment"].search(
            [("session_id", "=", self.session.id)]
        )
        accounts = self.session.mapped("payment_method_ids.receivable_account_id")
        self.assertEqual(
            sum(payments.mapped("amount")),
            sum(
                self.session.move_id.line_ids.filtered(
                    lambda r: r.account_id in accounts
                ).mapped("balance")
            ),
        )
