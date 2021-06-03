# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.cb_test.tests.test_cb import TestCB
from odoo.tests.common import at_install, post_install


@post_install(True)
@at_install(False)
class TestCBPayment(TestCB):
    def test_down_payments(self):
        self.plan_definition2.third_party_bill = False
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        invoice = (
            self.env["wizard.medical.encounter.add.amount"]
            .create(
                {
                    "encounter_id": encounter.id,
                    "pos_session_id": self.session.id,
                    "journal_id": self.journal_1[0].id,
                    "amount": 200,
                }
            )
            ._run()
        )
        self.assertEqual(invoice.type, "out_invoice")
        invoice = (
            self.env["wizard.medical.encounter.add.amount"]
            .create(
                {
                    "encounter_id": encounter.id,
                    "pos_session_id": self.session.id,
                    "journal_id": self.journal_1[0].id,
                    "amount": -100,
                }
            )
            ._run()
        )
        self.assertEqual(invoice.type, "out_refund")
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertEqual(encounter.pending_private_amount, 0)
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "journal_id": self.journal_1[0].id,
            }
        ).run()
        sale_order = encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment
        )
        self.assertTrue(sale_order)
        self.assertEqual(sale_order.amount_total, 0)
