from odoo.addons.cb_medical_pos.tests import common


class TestPosValidation(common.MedicalSavePointCase):
    def test_change_partner(self):
        self.company.change_partner_journal_id = self.env[
            "account.journal"
        ].create(
            {
                "name": "Change patient Journal",
                "code": "CHANGE",
                "company_id": self.company.id,
                "type": "general",
            }
        )
        self.plan_definition2.third_party_bill = False
        # self.plan_definition.is_billable = True
        self.agreement_line3.coverage_percentage = 0
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "payment_method_id": self.payment_method_id.id,
            }
        ).run()
        self.assertEqual(
            1, len(encounter.sale_order_ids.mapped("invoice_ids"))
        )
        partner = self.env["res.partner"].create({"name": "New Partner"})
        self.env["medical.encounter.change.partner"].create(
            {"encounter_id": encounter.id, "partner_id": partner.id}
        ).run()
        self.assertEqual(
            3, len(encounter.sale_order_ids.mapped("invoice_ids"))
        )
        self.assertTrue(
            encounter.sale_order_ids.mapped("invoice_ids").filtered(
                lambda r: r.partner_id == partner
            )
        )
        partner_2 = self.env["res.partner"].create({"name": "New Partner 2"})
        self.env["medical.encounter.change.partner"].create(
            {"encounter_id": encounter.id, "partner_id": partner_2.id}
        ).run()
        self.assertEqual(
            5, len(encounter.sale_order_ids.mapped("invoice_ids"))
        )
        self.assertEqual(
            2,
            len(
                encounter.sale_order_ids.mapped("invoice_ids").filtered(
                    lambda r: r.partner_id == partner
                )
            ),
        )
        self.assertTrue(
            encounter.sale_order_ids.mapped("invoice_ids").filtered(
                lambda r: r.partner_id == partner_2
            )
        )

    def test_set_self_invoice(self):
        partner = self.env["res.partner"].create({"name": "New Partner"})
        self.assertFalse(partner.self_invoice)
        self.assertFalse(partner.self_invoice_refund_sequence_id)
        partner.set_self_invoice()
        self.assertTrue(partner.self_invoice)
        self.assertTrue(partner.self_invoice_refund_sequence_id)
        sequence_1 = partner.self_invoice_refund_sequence_id
        partner.set_self_invoice()
        sequence_2 = partner.self_invoice_refund_sequence_id
        self.assertTrue(partner.self_invoice_refund_sequence_id)
        self.assertEqual(sequence_1, sequence_2)

    def test_invoice_validate(self):
        partner = self.env["res.partner"].create({"name": "New Partner"})
        partner.set_self_invoice()
        invoice = self.env["account.move"].create(
            {
                "partner_id": partner.id,
                "set_self_invoice": True,
                "type": "in_refund",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test",
                            "product_id": self.product_01.id,
                            "price_unit": 100.0,
                            "account_id": self.bank_account.id,
                        },
                    )
                ],
            }
        )
        self.assertFalse(invoice.self_invoice_number)
        invoice.post()
        self.assertEqual(invoice.state, "posted")
        self.assertTrue(invoice.self_invoice_number)
