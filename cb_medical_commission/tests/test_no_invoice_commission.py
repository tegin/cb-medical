from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestNoInvoiceCommission(TransactionCase):
    def setUp(self):
        super().setUp()
        self.commission = self.env["sale.commission"].create(
            {
                "name": "10% fixed commission (Net amount) - Invoice Based",
                "fix_qty": 10.0,
                "amount_base_type": "net_amount",
            }
        )
        self.agent = self.create_agent("Agent 01")
        self.partner = self.env["res.partner"].create(
            {"name": "Partner", "customer_rank": True}
        )
        self.product = self.env["product.product"].create(
            {"name": "Product", "type": "service"}
        )
        self.group = self.browse_ref("cb_medical_careplan_sale.no_invoice")

    def create_agent(self, name):
        return self.env["res.partner"].create(
            {"name": name, "agent": True, "commission_id": self.commission.id}
        )

    def test_no_invoice_commission(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "invoice_group_method_id": self.group.id,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "price_unit": self.product.lst_price,
                            "agent_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "agent_id": self.agent.id,
                                        "commission_id": self.agent.commission_id.id,
                                    },
                                )
                            ],
                        },
                    )
                ],
            }
        )
        self.assertTrue(sale_order.order_line.agent_ids.settled)
        sale_order.action_confirm()
        self.assertFalse(sale_order.order_line.agent_ids.settled)
        wizard = self.env["sale.commission.no.invoice.make.settle"].create(
            {"date_to": fields.Datetime.now() + relativedelta(months=1)}
        )
        settlements = self.env["sale.commission.settlement"].browse(
            wizard.action_settle()["domain"][0][2]
        )
        self.assertTrue(settlements)

    def test_invoice_commission(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "price_unit": self.product.lst_price,
                            "agent_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "agent_id": self.agent.id,
                                        "commission_id": self.agent.commission_id.id,
                                    },
                                )
                            ],
                        },
                    )
                ],
            }
        )
        self.assertTrue(sale_order.order_line.agent_ids.settled)
        sale_order.action_confirm()
        self.assertTrue(sale_order.order_line.agent_ids.settled)
        wizard = self.env["sale.commission.no.invoice.make.settle"].create(
            {
                "date_to": (
                    fields.Datetime.from_string(fields.Datetime.now())
                    + relativedelta(months=1)
                )
            }
        )
        self.assertNotIn("domain", wizard.action_settle())
