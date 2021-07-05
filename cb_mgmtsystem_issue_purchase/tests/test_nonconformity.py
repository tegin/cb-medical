# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import TransactionCase


class TestNonconformityEncounter(TransactionCase):
    def setUp(self):
        super(TestNonconformityEncounter, self).setUp()
        self.origin = self.env["mgmtsystem.nonconformity.origin"].create(
            {
                "name": "origin",
                "responsible_user_id": self.env.uid,
                "manager_user_id": self.env.uid,
            }
        )
        self.product = self.env["product.product"].create({"name": "PRODUCT"})
        self.order = self.env["purchase.order"].create(
            {
                "partner_id": self.env.user.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_qty": 1,
                            "date_planned": fields.Datetime.now(),
                            "product_uom": self.product.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )

    def test_nonconformity(self):
        wizard = (
            self.env["wizard.create.nonconformity"]
            .with_context(
                active_id=self.order.id, active_model=self.order._name
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
                ("res_id", "=", self.order.id),
                ("res_model", "=", self.order._name),
            ]
        )
        self.assertTrue(issue)
        issue.to_nonconformity()
        self.assertEqual(issue.non_conformity_id.res_id, self.order.id)
        self.order.action_view_quality_issues()
