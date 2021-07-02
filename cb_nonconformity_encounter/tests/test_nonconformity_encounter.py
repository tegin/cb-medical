# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestNonconformityEncounter(TransactionCase):
    def setUp(self):
        super(TestNonconformityEncounter, self).setUp()
        self.partner_id = self.env["res.partner"].create({"name": "Partner"})
        self.origin = self.env["mgmtsystem.nonconformity.origin"].create(
            {
                "name": "origin",
                "from_encounter": True,
                "responsible_user_id": self.env.uid,
                "manager_user_id": self.env.uid,
            }
        )
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id}
        )

    def test_wizard_nonconformity_encounter(self):
        wizard = (
            self.env["wizard.create.nonconformity.encounter"]
            .with_context(
                active_id=self.encounter.id, active_model=self.encounter._name
            )
            .create(
                {
                    "name": "Title",
                    "description": "Description",
                    "origin_id": self.origin.id,
                }
            )
        )
        wizard.flush()
        self.assertEqual(
            wizard.partner_id, self.encounter.patient_id.partner_id
        )
        action = wizard.create_quality_issue()
        issue = self.env[action["res_model"]].browse(action["res_id"])
        self.assertTrue(issue)
        issue.to_nonconformity()
        # "partner_id": self.partner_id.id,
        self.assertEqual(issue.non_conformity_id.res_id, self.encounter.id)
