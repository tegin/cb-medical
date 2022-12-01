from datetime import timedelta

from odoo import fields

from odoo.addons.cb_medical_careplan_sale.tests import common


class TestCBInvoicing(common.MedicalSavePointCase):
    def test_multiple_groups(self):
        method = self.browse_ref("cb_medical_careplan_sale.by_patient")
        method_2 = self.browse_ref("cb_medical_careplan_sale.by_customer")
        auth_method = self.env["medical.authorization.method"].create(
            {
                "name": "Testing authorization_method",
                "code": "none",
                "invoice_group_method_id": method_2.id,
                "always_authorized": True,
            }
        )
        self.agreement_line.write(
            {
                "authorization_method_id": auth_method.id,
                "coverage_percentage": 100,
            }
        )
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        encounters = self.env["medical.encounter"]
        for _ in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            encounters |= encounter
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(group.is_sellable_insurance or group.is_sellable_private)
            self.assertEqual(method, group.invoice_group_method_id)
            self.assertFalse(
                self.env["medical.request.group"].search(
                    [
                        ("encounter_id", "=", encounter.id),
                        ("careplan_id", "=", careplan.id),
                        ("invoice_group_method_id", "=", method_2.id),
                    ]
                )
            )
            wizard = self.env["medical.careplan.add.plan.definition"].create(
                {
                    "careplan_id": careplan.id,
                    "agreement_line_id": self.agreement_line.id,
                }
            )
            self.assertIn(self.agreement, wizard.agreement_ids)
            self.action.is_billable = False
            wizard.run()
            self.assertFalse(group.third_party_bill)
            self.assertTrue(
                self.env["medical.request.group"].search(
                    [
                        ("encounter_id", "=", encounter.id),
                        ("careplan_id", "=", careplan.id),
                        ("invoice_group_method_id", "=", method_2.id),
                    ]
                )
            )
            encounter.create_sale_order()
            self.assertTrue(encounter.sale_order_ids)
            for sale_order in encounter.sale_order_ids:
                self.assertFalse(sale_order.third_party_order)
        for encounter in encounters:
            encounter.sale_order_ids.action_confirm()
            for line in encounter.sale_order_ids.mapped("order_line"):
                line.qty_delivered = line.product_uom_qty
            encounter.sale_order_ids.with_context(
                active_model=encounter.sale_order_ids._name
            )._create_invoices()
        wzd = self.env["invoice.sales.by.group"].create(
            {
                "invoice_group_method_id": method_2.id,
                "customer_ids": [(4, self.payor.id)],
                "date_to": fields.Date.today() + timedelta(days=1),
            }
        )
        wzd.invoice_sales_by_group()
        for encounter in encounters:
            for sale_order in encounter.sale_order_ids:
                self.assertTrue(
                    all(line.invoice_lines for line in sale_order.order_line)
                )

    def test_no_invoice(self):
        method = self.browse_ref("cb_medical_careplan_sale.no_invoice")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        sale_orders = self.env["sale.order"]
        for _ in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(group.is_sellable_insurance or group.is_sellable_private)
            self.assertFalse(group.third_party_bill)
            encounter.create_sale_order()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            sale_order.action_confirm()
            sale_orders |= sale_order
        for line in sale_orders.mapped("order_line"):
            self.assertEqual(line.qty_to_invoice, 0)

    def test_monthly_invoice(self):
        method = self.browse_ref("cb_medical_careplan_sale.by_customer")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        nomenclature_product = self.env["product.nomenclature.product"].create(
            {
                "nomenclature_id": self.nomenclature.id,
                "product_id": self.agreement_line3.product_id.id,
                "name": "nomenclature_name",
                "code": "nomenclature_code",
            }
        )
        sale_orders = self.env["sale.order"]
        for _i in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(group.is_sellable_insurance or group.is_sellable_private)
            self.assertFalse(group.third_party_bill)
            encounter.create_sale_order()
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            sale_order.action_confirm()
            for line in sale_order.mapped("order_line"):
                line.qty_delivered = line.product_uom_qty
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            sale_orders |= sale_order
            sale_order.flush()
        action = (
            self.env["invoice.sales.by.group"]
            .create(
                {
                    "invoice_group_method_id": method.id,
                    "customer_ids": [(4, self.payor.id)],
                    "date_to": fields.Date.today() + timedelta(days=-1),
                    "company_ids": [(6, 0, self.company.ids)],
                }
            )
            .invoice_sales_by_group()
        )
        self.assertFalse(action)
        action = (
            self.env["invoice.sales.by.group"]
            .create(
                {
                    "invoice_group_method_id": method.id,
                    "customer_ids": [(4, self.payor.id)],
                    "date_to": fields.Date.today() + timedelta(days=1),
                    "company_ids": [(6, 0, self.company.ids)],
                }
            )
            .invoice_sales_by_group()
        )
        self.assertTrue(action.get("res_id", False))
        invoice = self.env[action["res_model"]].browse(action.get("res_id", False))
        invoice._post()
        for line in invoice.invoice_line_ids:
            self.assertEqual(line.name, nomenclature_product.name)
        for sale_order in sale_orders:
            self.assertTrue(sale_order.invoice_status == "invoiced")

    def test_preinvoice_no_invoice(self):
        method = self.browse_ref("cb_medical_careplan_sale.no_invoice_preinvoice")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        sale_orders = self.env["sale.order"]
        encounters = self.env["medical.encounter"]
        for _i in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            encounters |= encounter
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(group.is_sellable_insurance or group.is_sellable_private)
            self.assertFalse(group.third_party_bill)
            encounter.create_sale_order()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            sale_orders |= sale_order
        preinvoice_obj = self.env["sale.preinvoice.group"]
        self.assertFalse(
            preinvoice_obj.search([("agreement_id", "=", self.agreement.id)])
        )
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.payor.ids)],
            }
        ).run()
        self.assertFalse(
            preinvoice_obj.search([("agreement_id", "=", self.agreement.id)])
        )
        for sale_order in sale_orders:
            sale_order.action_confirm()
            for line in sale_order.order_line:
                line.qty_delivered = line.product_uom_qty
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.payor.ids)],
            }
        ).run()
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertTrue(preinvoices)
        for preinvoice in preinvoices:
            self.assertTrue(preinvoice.non_validated_line_ids)
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            preinvoice.close_sorting()
            self.assertTrue(preinvoice.non_validated_line_ids)
            preinvoice.close()
            self.assertFalse(preinvoice.non_validated_line_ids)
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertFalse(preinvoices)
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.payor.ids)],
            }
        ).run()
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertTrue(preinvoices)
        invoice_obj = self.env["account.move"]
        self.assertFalse(invoice_obj.search([("partner_id", "=", self.payor.id)]))
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            for encounter in encounters:
                result = preinvoice.scan_barcode_preinvoice(
                    encounter.internal_identifier
                )
                self.assertEqual(result["context"]["default_state"], "waiting")
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertFalse(preinvoice.move_id)
        invoices = invoice_obj.search(
            [("partner_id", "in", [self.payor.id, self.sub_payor.id])]
        )
        self.assertFalse(invoices)
