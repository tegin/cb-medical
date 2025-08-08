# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.cb_medical_careplan_sale.tests import common


class TestAccountPortalCommission(common.MedicalSavePointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.practitioner_01.write(
            {
                "agent": True,
                "commission_id": cls.env.ref("cb_medical_commission.commission_01").id,
            }
        )
        cls.practitioner_02.write(
            {
                "agent": True,
                "commission_id": cls.env.ref("cb_medical_commission.commission_01").id,
            }
        )
        cls.product_01.medical_commission = True
        cls.action.fixed_fee = 1

    def doCommissionEncountersWorkflow(self):
        """This method replies the workflow of the test test_monthly_invoice
        in cb_medical_commission module."""
        method = self.browse_ref("cb_medical_careplan_sale.by_customer")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        sale_orders = self.env["sale.order"]
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        encounter.create_sale_order()
        encounter.sale_order_ids.action_confirm()
        for line in encounter.sale_order_ids.mapped("order_line"):
            line.qty_delivered = line.product_uom_qty
        sale_order = encounter.sale_order_ids
        sale_orders |= sale_order
        sale_order.flush_recordset()
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
        invoice = self.env[action["res_model"]].browse(action.get("res_id", False))
        invoice.action_post()
        for request in encounter.careplan_ids.procedure_request_ids:
            request.draft2active()
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_01
        encounter.recompute_commissions()
        # Settle the payments
        self.env["commission.make.settle"].create(
            {
                "date_to": fields.Datetime.now() + relativedelta(months=1),
                "settlement_type": "sale_invoice",
            }
        )
        for request in encounter.careplan_ids.mapped(
            "procedure_request_ids"
        ).with_context(test_settle_integrity=True):
            procedure = request.procedure_ids
            procedure.check_commission()

        return encounter

    def test_search_encounter(self):
        self.practitioner_01.user_id = self.env["res.users"].create(
            {
                "name": "Test User 2",
                "login": "testuser2",
                "groups_id": [(4, self.env.ref("medical_base.group_medical_user").id)],
                "partner_id": self.practitioner_01.id,
            }
        )
        encounter = self.doCommissionEncountersWorkflow()
        self.assertTrue(encounter.id)

        search_wizard = self.env["search_encounters.wizard"].create(
            {"code": encounter.internal_identifier}
        )

        result = search_wizard.with_user(
            self.practitioner_01.user_id.id
        ).search_encounter()
        self.assertEqual(result["id"], encounter.id)
        self.assertEqual(result["internal_identifier"], encounter.internal_identifier)
        self.assertEqual(len(result["commissions"]), 1)
        self.assertEqual(result["commissions"][0]["name"], "Medical visit")
