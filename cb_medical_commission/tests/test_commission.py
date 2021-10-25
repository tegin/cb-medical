from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.cb_medical_careplan_sale.tests import common


class TestCBMedicalCommission(common.MedicalSavePointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.practitioner_01.write(
            {
                "agent": True,
                "commission_id": cls.env.ref(
                    "cb_medical_commission.commission_01"
                ).id,
            }
        )
        cls.practitioner_02.write(
            {
                "agent": True,
                "commission_id": cls.env.ref(
                    "cb_medical_commission.commission_01"
                ).id,
            }
        )

    def test_practitioner_conditions(self):
        self.plan_definition2.write({"third_party_bill": False})
        self.plan_definition2.action_ids.write(
            {"variable_fee": 0, "fixed_fee": 10}
        )
        self.assertNotEqual(
            self.plan_definition2.action_ids.activity_definition_id.service_id,
            self.agreement_line3.product_id,
        )
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env["medical.practitioner.condition"].create(
            {
                "practitioner_id": self.practitioner_02.id,
                "variable_fee": 10,
                "fixed_fee": 0,
                "procedure_service_id": self.agreement_line3.product_id.id,
            }
        )
        self.assertEqual(self.agreement_line3.product_id, group.service_id)
        for request in group.procedure_request_ids:
            request.draft2active()
            procedure = request.generate_event()
            self.assertEqual(request.state, "active")
            procedure.performer_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_check_condition()
            self.assertFalse(procedure.practitioner_condition_id)
            self.assertEqual(request.variable_fee, 0)
            self.assertEqual(request.fixed_fee, 10)
            general_cond = self.env["medical.practitioner.condition"].create(
                {
                    "practitioner_id": self.practitioner_02.id,
                    "variable_fee": 10,
                    "fixed_fee": 0,
                }
            )
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, general_cond)
            self.assertEqual(procedure.variable_fee, 10)
            self.assertEqual(procedure.fixed_fee, 0)
            proc_cond = self.env["medical.practitioner.condition"].create(
                {
                    "practitioner_id": self.practitioner_02.id,
                    "variable_fee": 0,
                    "fixed_fee": 5,
                    "procedure_service_id": self.product_02.id,
                }
            )
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, proc_cond)
            self.assertEqual(procedure.variable_fee, 0)
            self.assertEqual(procedure.fixed_fee, 5)
            group_cond = self.env["medical.practitioner.condition"].create(
                {
                    "practitioner_id": self.practitioner_02.id,
                    "variable_fee": 0,
                    "fixed_fee": 15,
                    "service_id": self.product_04.id,
                }
            )
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, group_cond)
            self.assertEqual(procedure.variable_fee, 0)
            self.assertEqual(procedure.fixed_fee, 15)
            cond = self.env["medical.practitioner.condition"].create(
                {
                    "practitioner_id": self.practitioner_02.id,
                    "variable_fee": 0,
                    "fixed_fee": 0,
                    "service_id": self.product_04.id,
                    "procedure_service_id": self.product_02.id,
                }
            )
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, cond)
            self.assertEqual(procedure.variable_fee, 0)
            self.assertEqual(procedure.fixed_fee, 0)

    def test_careplan_sale(self):
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        careplan = self.env["medical.careplan"].new(
            {
                "patient_id": self.patient_01.id,
                "encounter_id": encounter.id,
                "coverage_id": self.coverage_01.id,
                "sub_payor_id": self.sub_payor.id,
            }
        )
        careplan._onchange_encounter()
        careplan = careplan.create(careplan._convert_to_write(careplan._cache))
        self.assertEqual(careplan.center_id, encounter.center_id)
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line.id,
            }
        )
        self.action.is_billable = False
        wizard.run()
        groups = self.env["medical.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertTrue(groups)
        medication_requests = self.env["medical.medication.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertEqual(careplan.state, "draft")
        self.assertFalse(medication_requests.filtered(lambda r: r.is_billable))
        self.assertTrue(
            groups.filtered(
                lambda r: r.child_model == "medical.medication.request"
            )
        )
        self.assertTrue(
            groups.filtered(
                lambda r: (r.is_sellable_insurance or r.is_sellable_private)
                and r.child_model == "medical.medication.request"
            )
        )
        self.assertTrue(
            groups.filtered(
                lambda r: r.is_billable
                and r.child_model == "medical.medication.request"
            )
        )
        encounter.create_sale_order()
        self.assertTrue(encounter.sale_order_ids)
        procedure_requests = self.env["medical.procedure.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertGreater(len(procedure_requests), 0)
        medication_requests = self.env["medical.medication.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertGreater(len(medication_requests), 0)
        for sale_order in encounter.sale_order_ids:
            sale_order.recompute_lines_agents()
            self.assertEqual(sale_order.commission_total, 0)
        procedure_requests = self.env["medical.procedure.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertGreater(len(procedure_requests), 0)
        for request in procedure_requests:
            self.assertEqual(request.center_id, encounter.center_id)
            self.assertEqual(request.state, "draft")
            procedure = request.generate_event()
            procedure.write({"performer_id": self.practitioner_01.id})
            procedure.performer_id = self.practitioner_02
            procedure.preparation2in_progress()
            procedure.in_progress2completed()
        for group in careplan.request_group_ids:
            self.assertEqual(group.state, "completed")
        encounter.recompute_commissions()
        self.assertTrue(encounter.sale_order_ids)
        for sale_order in encounter.sale_order_ids:
            self.assertTrue(sale_order.patient_name)
            original_patient_name = sale_order.patient_name
            patient_name = "{} {}".format(original_patient_name, "TEST")
            sale_order.patient_name = patient_name
            for line in sale_order.order_line:
                self.assertTrue(line.tax_id)
                self.assertEqual(line.patient_name, patient_name)
            line = sale_order.order_line[0]
            line.patient_name = original_patient_name
            self.assertEqual(sale_order.patient_name, original_patient_name)
            sale_order.recompute_lines_agents()
            self.assertGreater(sale_order.commission_total, 0)
            sale_order.flush()
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
        self.assertTrue(encounter.sale_order_ids)
        for sale_order in encounter.sale_order_ids:
            sale_order.action_confirm()
            self.assertIn(sale_order.state, ["done", "sale"])
        self.assertTrue(
            encounter.sale_order_ids.filtered(
                lambda r: r.preinvoice_status == "to preinvoice"
                and any(
                    line.invoice_group_method_id
                    == self.browse_ref(
                        "cb_medical_careplan_sale.by_preinvoicing"
                    )
                    for line in r.order_line
                )
            )
        )
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
        # Test cancellation of preinvoices
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.cancel()
            self.assertFalse(preinvoice.line_ids)
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
        # Test unlink of not validated order_lines
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
        self.assertFalse(
            invoice_obj.search([("partner_id", "=", self.payor.id)])
        )
        # Test barcodes
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            result = preinvoice.scan_barcode_preinvoice(
                encounter.internal_identifier
            )
            self.assertEqual(result["context"]["default_status_state"], 0)
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.move_id)
        invoices = invoice_obj.search(
            [("partner_id", "in", [self.payor.id, self.sub_payor.id])]
        )
        self.assertTrue(invoices)
        # Test invoice unlink
        for invoice in invoices:
            self.assertEqual(invoice.state, "draft")
            invoice.line_ids.unlink()
        for sale_order in encounter.sale_order_ids:
            for line in sale_order.order_line:
                self.assertFalse(line.preinvoice_group_id)
        # Test manual validation of lines on preinvoices
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
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            for line in preinvoice.line_ids:
                line.validate_line()
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.line_ids)
            self.assertTrue(preinvoice.move_id)
        invoices = invoice_obj.search(
            [
                ("partner_id", "in", [self.payor.id, self.sub_payor.id]),
                ("state", "=", "draft"),
            ]
        )
        self.assertTrue(invoices)
        # Invoices should be reused
        self.assertEqual(1, len(invoices))
        for invoice in invoices:
            self.assertGreater(invoice.commission_total, 0)
            invoice.recompute_lines_agents()
            self.assertGreater(invoice.commission_total, 0)

    def test_no_invoice(self):
        method = self.browse_ref("cb_medical_careplan_sale.no_invoice")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.company.sale_merge_draft_invoice = True
        sale_orders = self.env["sale.order"]
        encounters = self.env["medical.encounter"]
        for _ in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private
            )
            self.assertFalse(group.third_party_bill)
            encounter.create_sale_order()
            encounter.sale_order_ids.action_confirm()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            for line in sale_order.order_line:
                self.assertFalse(line.agent_ids)
            sale_orders |= sale_order
            encounters |= encounter
        for line in sale_orders.mapped("order_line"):
            self.assertEqual(line.qty_to_invoice, 0)
        for encounter in encounters:
            self.assertTrue(
                encounter.mapped("careplan_ids.procedure_request_ids")
            )
            for request in encounter.mapped(
                "careplan_ids.procedure_request_ids"
            ):
                request.draft2active()
                self.assertEqual(request.center_id, encounter.center_id)
                procedure = request.generate_event()
                procedure.performer_id = self.practitioner_02
            encounter.refresh()
            encounter.recompute_commissions()
            encounter.refresh()
            for line in encounter.sale_order_ids.mapped("order_line"):
                self.assertTrue(line.agent_ids)
        # Settle the payments
        wizard = self.env["sale.commission.no.invoice.make.settle"].create(
            {
                "date_to": (
                    fields.Datetime.from_string(fields.Datetime.now())
                    + relativedelta(months=1)
                )
            }
        )
        settlements = self.env["sale.commission.settlement"].browse(
            wizard.action_settle()["domain"][0][2]
        )
        self.assertTrue(settlements)
        for encounter in encounters:
            for request in encounter.careplan_ids.mapped(
                "procedure_request_ids"
            ):
                procedure = request.procedure_ids
                self.assertEqual(len(procedure.sale_agent_ids), 1)
                self.assertEqual(len(procedure.invoice_agent_ids), 0)
                procedure.performer_id = self.practitioner_01
                procedure.check_commission()
                self.assertEqual(len(procedure.sale_agent_ids), 3)
                self.assertEqual(len(procedure.invoice_agent_ids), 0)

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
        self.company.sale_merge_draft_invoice = True
        sale_orders = self.env["sale.order"]
        encounters = self.env["medical.encounter"]
        for _i in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private
            )
            self.assertFalse(group.third_party_bill)
            encounter.create_sale_order()
            encounter.sale_order_ids.action_confirm()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            for line in sale_order.order_line:
                self.assertFalse(line.agent_ids)
            sale_orders |= sale_order
            encounters |= encounter
            sale_order.flush()
        action = (
            self.env["invoice.sales.by.group"]
            .create(
                {
                    "invoice_group_method_id": method.id,
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
        invoice = self.env[action["res_model"]].browse(
            action.get("res_id", False)
        )
        invoice.post()
        for line in invoice.invoice_line_ids:
            self.assertEqual(line.name, nomenclature_product.name)
        for sale_order in sale_orders:
            self.assertTrue(sale_order.invoice_status == "invoiced")
        for encounter in encounters:
            for request in encounter.careplan_ids.mapped(
                "procedure_request_ids"
            ):
                request.draft2active()
                self.assertEqual(request.center_id, encounter.center_id)
                procedure = request.generate_event()
                procedure.performer_id = self.practitioner_02
            encounter.recompute_commissions()
            for line in encounter.sale_order_ids.mapped("order_line"):
                self.assertTrue(line.agent_ids)
        # Settle the payments
        wizard = self.env["sale.commission.make.settle"].create(
            {"date_to": fields.Datetime.now() + relativedelta(months=1)}
        )
        settlements = self.env["sale.commission.settlement"].browse(
            wizard.action_settle()["domain"][0][2]
        )
        self.assertTrue(settlements)
        for encounter in encounters:
            for request in encounter.careplan_ids.mapped(
                "procedure_request_ids"
            ):
                procedure = request.procedure_ids
                self.assertEqual(len(procedure.sale_agent_ids), 1)
                self.assertEqual(len(procedure.invoice_agent_ids), 1)
                procedure.performer_id = self.practitioner_01
                procedure.check_commission()
                self.assertEqual(len(procedure.sale_agent_ids), 1)
                self.assertEqual(len(procedure.invoice_agent_ids), 3)

    def test_sale_laboratory(self):
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.lab_activity.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": False,
                "name": "Action4",
                "performer_id": self.practitioner_01.id,
            }
        )

        self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.product_07.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 0.0,
                "coverage_percentage": 50.0,
                "authorization_method_id": self.browse_ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        lab_req = group.laboratory_request_ids
        event = lab_req.generate_event(
            {
                "is_sellable_private": True,
                "is_sellable_insurance": True,
                "private_amount": 20,
                "coverage_amount": 10,
                "private_cost": 10,
                "coverage_cost": 5,
            }
        )
        self.assertEqual(event.performer_id, self.practitioner_01)
        encounter.create_sale_order()
        encounter.recompute_commissions()
        encounter.refresh()
        self.assertTrue(
            encounter.sale_order_ids.mapped("order_line").filtered(
                lambda r: r.medical_model == "medical.laboratory.event"
            )
        )
        for line in encounter.sale_order_ids.mapped("order_line").filtered(
            lambda r: r.medical_model == "medical.laboratory.event"
        ):
            action = line.open_medical_record()
            self.assertEqual(
                event, self.env[action["res_model"]].browse(action["res_id"])
            )
        self.assertEqual(
            len(
                encounter.sale_order_ids.mapped("order_line").filtered(
                    lambda r: r.medical_model == "medical.laboratory.event"
                )
            ),
            2,
        )
        self.assertTrue(
            encounter.sale_order_ids.mapped("order_line")
            .filtered(lambda r: r.medical_model == "medical.laboratory.event")
            .mapped("agent_ids")
        )
        self.assertGreater(
            sum(
                a.amount
                for a in encounter.sale_order_ids.mapped("order_line")
                .filtered(
                    lambda r: r.medical_model == "medical.laboratory.event"
                )
                .mapped("agent_ids")
            ),
            0,
        )
        self.assertEqual(encounter.invoice_count, 0)
        sale_orders = encounter.sale_order_ids
        for sale_order in sale_orders:
            sale_order.action_confirm()
            if sale_order.invoice_group_method_id == self.env.ref(
                "cb_medical_careplan_sale.by_preinvoicing"
            ):
                continue
            sale_order.with_context(
                active_model=sale_order._name
            )._create_invoices()
        self.assertEqual(encounter.invoice_count, 2)
        self.assertGreater(
            sum(
                a.amount
                for a in encounter.mapped(
                    "sale_order_ids.invoice_ids.invoice_line_ids.agent_ids"
                ).filtered(lambda r: r.laboratory_event_id)
            ),
            0,
        )
