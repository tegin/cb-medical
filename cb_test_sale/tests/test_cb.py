# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.cb_test.tests.test_cb import TestCB
from odoo.exceptions import ValidationError
from odoo.tests.common import at_install, post_install


@post_install(True)
@at_install(False)
class TestCBSale(TestCB):
    def test_careplan_sale_fail(self):
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
        self.env["wizard.medical.encounter.add.amount"].create(
            {
                "encounter_id": encounter.id,
                "amount": 10,
                "pos_session_id": self.session.id,
                "journal_id": self.session.journal_ids[0].id,
            }
        ).run()
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line.id,
            }
        )
        with self.assertRaises(ValidationError):
            wizard.run()

    def test_careplan_sale(self):
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        encounter_02 = self.env["medical.encounter"].create(
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
        invoice = (
            self.env["wizard.medical.encounter.add.amount"]
            .create(
                {
                    "encounter_id": encounter.id,
                    "amount": 10,
                    "pos_session_id": self.session.id,
                    "journal_id": self.session.journal_ids[0].id,
                }
            )
            ._run()
        )
        for line in invoice.invoice_line_ids:
            self.assertNotEqual(line.name, "/")
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line.id,
            }
        )
        self.action.is_billable = False
        wizard.run()
        self.assertTrue(self.session.action_view_sale_orders()["res_id"])
        groups = self.env["medical.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertTrue(groups)
        medication_requests = self.env["medical.medication.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertEqual(careplan.state, "draft")
        self.assertTrue(medication_requests.filtered(lambda r: r.is_billable))
        self.assertTrue(
            medication_requests.filtered(
                lambda r: r.is_sellable_insurance or r.is_sellable_private
            )
        )
        self.assertFalse(encounter.medication_item_ids)
        self.env["medical.encounter.medication"].create(
            {
                "medical_id": encounter.id,
                "product_id": self.product_03.id,
                "location_id": self.location.id,
            }
        ).run()
        self.assertTrue(encounter.medication_item_ids)
        self.env["medical.encounter.medication"].create(
            {
                "medical_id": encounter.id,
                "product_id": self.product_03.id,
                "location_id": self.location.id,
            }
        ).run()
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertTrue(encounter.sale_order_ids)
        self.assertTrue(encounter.has_preinvoicing)
        self.assertGreater(self.session.encounter_count, 0)
        self.assertGreater(self.session.sale_order_count, 0)
        self.assertEqual(
            self.session.action_view_encounters()["res_id"], encounter.id
        )
        journal = self.session.statement_ids.mapped("journal_id")[0]
        self.assertTrue(journal)
        self.assertGreater(encounter.pending_private_amount, 0)
        lines = len(
            self.session.statement_ids.filtered(
                lambda r: r.journal_id == journal
            ).mapped("line_ids")
        )
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "journal_id": journal.id,
            }
        ).run()
        invoice = encounter.sale_order_ids.filtered(
            lambda r: not r.coverage_agreement_id and not r.is_down_payment
        ).mapped("invoice_ids")
        for line in invoice.invoice_line_ids:
            self.assertNotEqual(line.name, "/")
        self.assertGreater(
            len(
                self.session.statement_ids.filtered(
                    lambda r: r.journal_id == journal
                ).mapped("line_ids")
            ),
            lines,
        )
        self.assertEqual(encounter.pending_private_amount, 0)
        self.session.action_pos_session_closing_control()
        self.assertTrue(self.session.invoice_ids)
        self.assertTrue(self.session.sale_order_line_ids)
        self.assertTrue(self.session.request_group_ids)
        self.assertTrue(self.session.down_payment_ids)
        self.session.action_pos_session_approve()
        self.assertEqual(self.session.validation_status, "in_progress")
        self.assertFalse(
            self.session.open_validation_encounter("TEST").get("res_id")
        )

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
            medicaments = self.env["sale.order.line"].search(
                [
                    ("order_id", "=", sale_order.id),
                    ("product_id", "=", self.service.id),
                ]
            )
            for medicament in medicaments:
                medicament_price = medicament.price_unit
                self.assertEqual(medicament_price, 20.0)
        procedure_requests = self.env["medical.procedure.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertGreater(len(procedure_requests), 0)
        for request in procedure_requests:
            self.assertEqual(request.center_id, encounter.center_id)
            self.assertEqual(request.state, "draft")
            procedure = request.generate_event()
            self.assertEqual(request.state, "active")
            procedure.write(
                {
                    "performer_id": self.practitioner_01.id,
                    "commission_agent_id": self.practitioner_01.id,
                }
            )
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02
            )
            procedure.preparation2in_progress()
            procedure.in_progress2completed()
            self.assertEqual(request.state, "completed")
        for group in careplan.request_group_ids:
            self.assertEqual(group.state, "completed")
        self.assertEqual(careplan.state, "completed")
        encounter.recompute_commissions()
        self.assertTrue(encounter.sale_order_ids)
        for sale_order in encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment
        ):
            self.assertTrue(sale_order.patient_name)
            original_patient_name = sale_order.patient_name
            patient_name = "{} {}".format(original_patient_name, "TEST")
            sale_order.patient_name = patient_name
            for line in sale_order.order_line:
                self.assertTrue(line.tax_id)
                self.assertEqual(
                    line.is_private, not bool(sale_order.coverage_agreement_id)
                )
                self.assertEqual(line.patient_name, patient_name)
            line = sale_order.order_line[0]
            line.patient_name = original_patient_name
            self.assertEqual(sale_order.patient_name, original_patient_name)
            sale_order.recompute_lines_agents()
            self.assertGreater(sale_order.commission_total, 0)
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
        invoice_obj = self.env["account.invoice"]
        self.assertFalse(
            invoice_obj.search([("partner_id", "=", self.payor.id)])
        )
        # Test barcodes
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            barcode = self.env["wizard.sale.preinvoice.group.barcode"].create(
                {"preinvoice_group_id": preinvoice.id}
            )
            barcode.on_barcode_scanned(encounter.internal_identifier)
            self.assertEqual(barcode.status_state, 0)
            barcode.on_barcode_scanned("No Barcode")
            self.assertEqual(barcode.status_state, 1)
            barcode.on_barcode_scanned(encounter_02.internal_identifier)
            self.assertEqual(barcode.status_state, 1)
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.invoice_id)
        invoices = invoice_obj.search(
            [("partner_id", "in", [self.payor.id, self.sub_payor.id])]
        )
        self.assertTrue(invoices)
        # Test invoice unlink
        for invoice in invoices:
            self.assertEqual(invoice.state, "draft")
            invoice.invoice_line_ids.unlink()
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
            self.assertTrue(preinvoice.invoice_id)
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

    def test_change_partner(self):
        self.company.change_partner_journal_id = self.env[
            "account.journal"
        ].create(
            {
                "name": "Change paChange patient Journal",
                "code": "CHANGE",
                "company_id": self.company.id,
                "type": "general",
            }
        )
        self.plan_definition2.third_party_bill = False
        # self.plan_definition.is_billable = True
        self.agreement_line3.coverage_percentage = 0
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        journal = self.session.statement_ids.mapped("journal_id")[0]
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "journal_id": journal.id,
            }
        ).run()
        self.assertEqual(
            1, len(encounter.sale_order_ids.mapped("invoice_ids"))
        )
        partner = self.env["res.partner"].create({"name": "New Partner"})
        self.env["medical.encounter.change.partner"].create(
            {"encounter_id": encounter.id, "partner_id": partner.id}
        ).run()
        self.assertEqual(
            3, len(encounter.sale_order_ids.mapped("invoice_ids"))
        )
        self.assertTrue(
            encounter.sale_order_ids.mapped("invoice_ids").filtered(
                lambda r: r.partner_id == partner
            )
        )
        partner_2 = self.env["res.partner"].create({"name": "New Partner 2"})
        self.env["medical.encounter.change.partner"].create(
            {"encounter_id": encounter.id, "partner_id": partner_2.id}
        ).run()
        self.assertEqual(
            5, len(encounter.sale_order_ids.mapped("invoice_ids"))
        )
        self.assertEqual(
            2,
            len(
                encounter.sale_order_ids.mapped("invoice_ids").filtered(
                    lambda r: r.partner_id == partner
                )
            ),
        )
        self.assertTrue(
            encounter.sale_order_ids.mapped("invoice_ids").filtered(
                lambda r: r.partner_id == partner_2
            )
        )

    def test_discount(self):
        method = self.browse_ref("cb_medical_careplan_sale.no_invoice")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.company.sale_merge_draft_invoice = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertFalse(group.medical_sale_discount_id)
        discount = self.env["medical.request.group.discount"].new(
            {"request_group_id": group.id}
        )
        discount.medical_sale_discount_id = self.discount
        discount._onchange_discount()
        discount.run()
        self.assertEqual(discount.discount, self.discount.percentage)
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertEqual(sale_order.amount_total, 50)
        self.assertEqual(sale_order.order_line.discount, 50)

    def test_careplan_add_function(self):
        encounter_action = self.env["medical.encounter"].create_encounter(
            patient=self.patient_01.id,
            center=self.center.id,
            careplan_data=[
                {
                    "coverage": self.coverage_01.id,
                    "service": self.agreement_line3.product_id.id,
                }
            ],
        )
        encounter = self.env["medical.encounter"].browse(
            encounter_action["res_id"]
        )
        self.assertTrue(encounter)
        self.assertTrue(encounter.careplan_ids)
        self.assertTrue(encounter.careplan_ids.request_group_ids)

    def test_careplan_add_wizard(self):
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        careplan_wizard = (
            self.env["medical.encounter.add.careplan"]
            .with_context(default_encounter_id=encounter.id)
            .new({"coverage_id": self.coverage_01.id})
        )
        careplan_wizard.onchange_coverage()
        careplan_wizard.onchange_coverage_template()
        careplan_wizard.onchange_payor()
        careplan_wizard = careplan_wizard.create(
            careplan_wizard._convert_to_write(careplan_wizard._cache)
        )
        self.assertEqual(encounter, careplan_wizard.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard.center_id)
        careplan_wizard.run()
        careplan = encounter.careplan_ids
        careplan_wizard_2 = (
            self.env["medical.encounter.add.careplan"]
            .with_context(default_encounter_id=encounter.id)
            .new({"coverage_id": self.coverage_01.id})
        )
        careplan_wizard_2.onchange_coverage()
        careplan_wizard_2.onchange_coverage_template()
        careplan_wizard_2.onchange_payor()
        careplan_wizard_2 = careplan_wizard_2.create(
            careplan_wizard_2._convert_to_write(careplan_wizard_2._cache)
        )
        self.assertEqual(encounter, careplan_wizard_2.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard_2.center_id)
        cp_2 = careplan_wizard_2.run()
        self.assertEqual(cp_2, careplan)
        careplan_wizard_3 = (
            self.env["medical.encounter.add.careplan"]
            .with_context(default_encounter_id=encounter.id)
            .new({"coverage_id": self.coverage_02.id})
        )
        careplan_wizard_3.onchange_coverage()
        careplan_wizard_3.onchange_coverage_template()
        careplan_wizard_3.onchange_payor()
        careplan_wizard_3 = careplan_wizard_2.create(
            careplan_wizard_3._convert_to_write(careplan_wizard_3._cache)
        )
        self.assertEqual(encounter, careplan_wizard_3.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard_3.center_id)
        cp_3 = careplan_wizard_3.run()
        self.assertNotEqual(cp_3, careplan)

    def test_cancel_encounter(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env["medical.encounter.cancel"].create(
            {
                "encounter_id": encounter.id,
                "cancel_reason_id": self.reason.id,
                "cancel_reason": "testing purposes",
                "pos_session_id": self.session.id,
            }
        ).run()
        careplan.refresh()
        self.assertEqual(careplan.state, "cancelled")
        self.assertIn(encounter.state, ["onleave", "finished"])
