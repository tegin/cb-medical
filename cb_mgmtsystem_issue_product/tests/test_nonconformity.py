# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestNonconformityProduct(TransactionCase):
    def setUp(self):
        super(TestNonconformityProduct, self).setUp()
        self.origin = self.env["mgmtsystem.nonconformity.origin"].create(
            {
                "name": "origin",
                "responsible_user_id": self.env.uid,
                "manager_user_id": self.env.uid,
            }
        )
        self.product = self.env["product.template"].create({"name": "PRODUCT"})

    def test_non_conformity(self):
        wizard = (
            self.env["wizard.create.nonconformity"]
            .with_context(
                active_id=self.product.id, active_model=self.product._name
            )
            .create(
                {
                    "name": "Title",
                    "description": "Description",
                    "origin_id": self.origin.id,
                    "partner_id": self.env.user.partner_id.id,
                }
            )
        )
        wizard.create_quality_issue()
        issue = self.env["mgmtsystem.quality.issue"].search(
            [
                ("res_id", "=", self.product.id),
                ("res_model", "=", self.product._name),
            ]
        )
        self.assertTrue(issue)
        issue.to_nonconformity()
        self.assertEqual(issue.non_conformity_id.res_id, self.product.id)
        self.product.action_view_quality_issues()
