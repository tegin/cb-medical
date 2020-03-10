# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestNonconformityEncounter(TransactionCase):
    def setUp(self):
        super(TestNonconformityEncounter, self).setUp()
        self.origin = self.env["mgmtsystem.nonconformity.origin"].create(
            {
                "name": "origin",
                "from_encounter": True,
                "responsible_user_id": self.env.uid,
                "manager_user_id": self.env.uid,
            }
        )
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.encounter_id = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id}
        )

    def test_nonconformity_encounter(self):
        wizard = (
            self.env["wizard.create.nonconformity"]
            .with_context(active_id=self.encounter_id.id)
            .create(
                {
                    "name": "Title",
                    "description": "Description",
                    "origin_id": self.origin.id,
                }
            )
        )
        wizard.create_quality_issue()
        issue = self.env["mgmtsystem.quality.issue"].search(
            [("encounter_id", "=", self.encounter_id.id)]
        )
        self.assertTrue(issue)
        issue.to_nonconformity()
        self.assertTrue(
            issue.non_conformity_id.encounter_id.id, self.encounter_id.id
        )
        action = self.encounter_id.action_view_quality_issues()
        self.assertEqual(action["res_id"], issue.id)
