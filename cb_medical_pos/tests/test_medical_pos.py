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
        cls.pos_config.write({"session_sequence_prefix": "POS"})
        cls.pos_config.write({"session_sequence_prefix": "PS"})
        cls.pos_config.open_session_cb()
        cls.session = cls.pos_config.current_session_id
        cls.session.action_pos_session_open()

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
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
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
