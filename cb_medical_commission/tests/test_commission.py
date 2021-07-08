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
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            procedure._onchange_check_condition()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02
            )
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
