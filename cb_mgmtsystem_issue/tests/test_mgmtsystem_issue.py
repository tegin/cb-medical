# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMgmtsystemIssue(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_id = self.env["res.partner"].create({"name": "Partner"})
        self.origin = self.env["mgmtsystem.nonconformity.origin"].create(
            {
                "name": "origin",
                "notify_creator": True,
                "responsible_user_id": self.env.user.id,
                "manager_user_id": self.env.user.id,
            }
        )
        self.mgmtsys = self.env["mgmtsystem.nonconformity"].create(
            {
                "partner_id": self.partner_id.id,
                "manager_user_id": self.env.user.id,
                "description": "description",
                "responsible_user_id": self.env.user.id,
            }
        )
        self.issue = self.env["mgmtsystem.quality.issue"].create(
            {
                "name": "Title",
                "description": "Description",
                "partner_id": self.partner_id.id,
                "responsible_user_id": self.env.uid,
                "manager_user_id": self.env.uid,
                "res_model": self.partner_id._name,
                "origin_ids": [(4, self.origin.id)],
                "res_id": self.partner_id.id,
            }
        )

    def test_mgmtsystem_no_relation(self):
        self.assertFalse(self.mgmtsys.access_related_item())
        self.mgmtsys.res_model = self.partner_id._name
        self.assertFalse(self.mgmtsys.access_related_item())

    def test_mgmtsystem_issue_accept(self):
        self.issue.to_accepted()
        self.assertEqual(self.issue.state, "ok")
        self.issue.back_to_pending()
        self.assertEqual(self.issue.state, "pending")

    def test_mgmtsystem_issue_to_non_conformity(self):
        """We want to check that the information has been inherited properly"""
        action = self.issue.to_nonconformity()
        self.assertEqual(self.issue.state, "no_ok")
        self.assertEqual(self.issue.non_conformity_id.id, action["res_id"])
        non_conformity = self.env[action["res_model"]].browse(action["res_id"])
        related_action = non_conformity.access_related_item()
        self.assertTrue(related_action)
        self.assertEqual(
            self.partner_id,
            self.env[related_action["res_model"]].browse(
                related_action["res_id"]
            ),
        )
        self.assertEqual(self.issue.partner_id, non_conformity.partner_id)
        self.assertEqual(self.issue.origin_ids, non_conformity.origin_ids)

    def test_mgmtsystem_issue_access_related_item(self):
        related_action = self.issue.access_related_item()
        self.assertTrue(related_action)
        self.assertEqual(
            self.partner_id,
            self.env[related_action["res_model"]].browse(
                related_action["res_id"]
            ),
        )
        self.assertTrue(self.issue.access_related_item())

    def test_fail_access_related_item(self):
        self.assertTrue(self.issue.access_related_item())
        self.issue.res_id = False
        self.assertFalse(self.issue.access_related_item())
        self.issue.res_model = "non.existent.nodel"
        self.assertFalse(self.issue.access_related_item())

    def test_mgmtsystem_res_partner(self):
        self.assertEqual(self.partner_id.quality_issue_count, 1)
        self.partner_id.action_view_quality_issues()
        self.issue2 = self.env["mgmtsystem.quality.issue"].create(
            {
                "name": "Title",
                "description": "Description",
                "partner_id": self.partner_id.id,
                "responsible_user_id": self.env.uid,
                "manager_user_id": self.env.uid,
                "res_model": self.partner_id._name,
                "origin_ids": [(4, self.origin.id)],
                "res_id": self.partner_id.id,
            }
        )
        self.assertEqual(self.partner_id.quality_issue_count, 2)
        self.partner_id.action_view_quality_issues()

    def test_wizard_non_conformity(self):
        """Creating an issue"""
        wizard = (
            self.env["wizard.create.nonconformity"]
            .with_context(
                active_model=self.partner_id._name,
                active_ids=self.partner_id.ids,
                active_id=self.partner_id.id,
            )
            .create(
                {
                    "name": "DEMO QUALITY ISSUE",
                    "description": "DEMO QUALITY ISSUE",
                    "origin_id": self.origin.id,
                    "partner_id": self.partner_id.id,
                }
            )
        )
        action = wizard.create_quality_issue()
        issue = self.env[action["res_model"]].browse(action["res_id"])
        self.assertEqual(issue._name, "mgmtsystem.quality.issue")
        related_action = self.issue.access_related_item()
        self.assertTrue(related_action)
        self.assertEqual(
            self.partner_id,
            self.env[related_action["res_model"]].browse(
                related_action["res_id"]
            ),
        )
