# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import UserError
from odoo.tests.common import at_install, post_install

from odoo.addons.cb_test.tests.test_cb import TestCB


@post_install(True)
@at_install(False)
class TestCBValidation(TestCB):
    def setUp(self):
        super().setUp()
        self.cancel_reason = self.env["medical.cancel.reason"].create(
            {"name": "Testing cancel reason"}
        )

    def close_encounter(self, encounter):
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        if encounter.state == "finished":
            return
        journal = self.session.statement_ids.mapped("journal_id")[0]
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "journal_id": journal.id,
            }
        ).run()

    def test_validation_constrain(self):
        self.plan_definition2.write({"third_party_bill": False})
        self.agreement_line3.write({"coverage_percentage": 0})
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.close_encounter(encounter)
        self.session.action_pos_session_closing_control()
        self.session.action_pos_session_approve()
        with self.assertRaises(UserError):
            encounter.sale_order_ids.mapped("order_line").medical_cancel(
                self.cancel_reason
            )

    def test_cancel_service(self):
        self.plan_definition2.write({"third_party_bill": False})
        self.agreement_line3.write({"coverage_percentage": 100})
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.close_encounter(encounter)
        self.session.action_pos_session_closing_control()
        self.session.action_pos_session_approve()
        encounter.sale_order_ids.mapped("order_line").medical_cancel(
            self.cancel_reason
        )
        self.assertFalse(encounter.sale_order_ids.mapped("order_line"))
