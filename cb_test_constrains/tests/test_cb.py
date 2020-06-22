# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import at_install, post_install

from odoo.addons.cb_test.tests.test_cb import TestCB


@post_install(True)
@at_install(False)
class TestCBConstrains(TestCB):
    def test_no_agreement(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        with self.assertRaises(ValidationError):
            # Raises 'Agreement must be defined'
            group.breakdown()

    def test_no_breakdown(self):
        self.plan_definition.is_billable = True
        self.plan_definition.is_breakdown = False
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(group.is_billable)
        self.assertFalse(group.is_breakdown)
        with self.assertRaises(ValidationError):
            # Raises 'Cannot breakdown a not billable line'
            group.breakdown()

    def test_cancel_encounter_failure(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        careplan.draft2active()
        careplan.active2completed()
        with self.assertRaises(ValidationError):
            # Raises 'It is not cancelable' relating to the care plan
            self.env["medical.encounter.cancel"].create(
                {
                    "encounter_id": encounter.id,
                    "cancel_reason_id": self.reason.id,
                    "cancel_reason": "testing purposes",
                    "pos_session_id": self.session.id,
                }
            ).run()
