from odoo.addons.cb_medical_careplan_sale.tests import common


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
        cls.payment_method_id = cls.env["pos.payment.method"].create(
            {
                "name": "Payment method test",
                "receivable_account_id": cls.bank_account.id,
            }
        )
        pos_vals = (
            cls.env["pos.config"]
            .with_context(company_id=cls.company.id)
            .default_get(
                ["stock_location_id", "invoice_journal_id", "pricelist_id"]
            )
        )
        pos_vals.update(
            {
                "name": "Config",
                "payment_method_ids": cls.payment_method_id,
                "requires_approval": True,
                "company_id": cls.company.id,
                "crm_team_id": False,
            }
        )
        cls.pos_config = cls.env["pos.config"].create(pos_vals)
        cls.pos_config.open_session_cb()
        cls.session = cls.pos_config.current_session_id
        cls.session.action_pos_session_open()
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
        invoice = (
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
        for line in invoice.invoice_line_ids:
            self.assertNotEqual(line.name, "/")
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line.id,
            }
        )
        self.action.is_billable = False
        wizard.run()
        self.assertTrue(self.session.action_view_sale_orders()["res_id"])
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
        lines = len(
            self.env["pos.payment"].search(
                [("session_id", "=", self.session.id)]
            )
        )
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "payment_method_id": self.payment_method_id.id,
            }
        ).run()
        invoice = encounter.sale_order_ids.filtered(
            lambda r: not r.coverage_agreement_id and not r.is_down_payment
        ).mapped("invoice_ids")
        for line in invoice.invoice_line_ids:
            self.assertNotEqual(line.name, "/")
        self.assertGreater(
            len(
                self.env["pos.payment"].search(
                    [("session_id", "=", self.session.id)]
                )
            ),
            lines,
        )
        self.assertEqual(encounter.pending_private_amount, 0)
        self.session.action_pos_session_closing_control()
        self.assertTrue(
            self.env["pos.payment"]
            .search([("session_id", "=", self.session.id)])
            .mapped("pos_order_id.account_move")
        )
        # self.assertTrue(self.session.sale_order_line_ids)
        # self.assertTrue(self.session.request_group_ids)
        # self.assertTrue(self.session.down_payment_ids)
        self.session.action_pos_session_approve()
        invoices = encounter.sale_order_ids.invoice_ids
        self.assertTrue(invoices)
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
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02
            )
        self.practitioner_02.third_party_sequence_id = self.env[
            "ir.sequence"
        ].create({"name": "sequence"})
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertEqual(encounter.pending_private_amount, 0)
        extra_order = encounter.sale_order_ids.filtered(
            lambda r: r.is_down_payment and r.state == "draft"
        )
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
        self.assertFalse(
            payments.filtered(
                lambda r: r.pos_order_id.account_move in sale_order.invoice_ids
            )
        )
        self.assertTrue(
            payments.filtered(
                lambda r: r.pos_order_id.account_move
                in extra_order.invoice_ids
            )
        )
        self.assertEqual(
            -100,
            sum(
                p.amount
                for p in payments.filtered(
                    lambda r: r.pos_order_id.account_move
                    in extra_order.invoice_ids
                )
            ),
        )
        sale_order = encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment and r.third_party_partner_id
        )
        self.assertTrue(sale_order)
        payments = payments.filtered(
            lambda r: r.pos_order_id.sale_order_id in sale_order
        )
        self.assertTrue(payments)
        self.assertEqual(100, sum(p.amount for p in payments))
        self.assertEqual(sum(s.amount_total for s in sale_order), 100)
        self.session.action_pos_session_approve()
        invoices = encounter.sale_order_ids.invoice_ids
        self.assertTrue(invoices)
        for invoice in invoices:
            self.assertEqual(0, invoice.amount_residual)

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
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02
            )
        self.practitioner_02.third_party_sequence_id = self.env[
            "ir.sequence"
        ].create({"name": "sequence"})
        self.assertTrue(
            group.is_sellable_insurance or group.is_sellable_private
        )
        self.assertTrue(group.third_party_bill)
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertGreater(encounter.sale_order_count, 0)
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertTrue(sale_order.third_party_order)
        self.assertEqual(
            sale_order.third_party_partner_id, self.practitioner_02
        )
        self.assertGreater(encounter.pending_private_amount, 0)
        self.assertGreater(sum(encounter.sale_order_ids.mapped("residual")), 0)
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
        accounts = self.session.mapped(
            "payment_method_ids.receivable_account_id"
        )
        self.assertEqual(
            sum(payments.mapped("amount")),
            sum(
                self.session.move_id.line_ids.filtered(
                    lambda r: r.account_id in accounts
                ).mapped("balance")
            ),
        )
        self.assertEqual(sum(encounter.sale_order_ids.mapped("residual")), 0)
