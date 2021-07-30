from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.cb_medical_pos.tests import common
from odoo.exceptions import UserError, ValidationError


class TestPosValidation(common.MedicalSavePointCase):
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
        cls.cancel_reason = cls.env["medical.cancel.reason"].create(
            {"name": "Testing cancel reason"}
        )

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
        self.company.sale_merge_draft_invoice = True
        for _ in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private
            )
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
            encounter.refresh()
            self.env["wizard.medical.encounter.close"].create(
                {
                    "encounter_id": encounter.id,
                    "pos_session_id": self.session.id,
                }
            ).run()
            self.assertTrue(encounter.sale_order_ids)
            self.assertEqual(2, len(encounter.sale_order_ids))
            for sale_order in encounter.sale_order_ids:
                self.assertFalse(sale_order.third_party_order)
                for line in sale_order.order_line:
                    self.assertFalse(line.agent_ids)
        self.session.action_pos_session_close()
        self.assertTrue(self.session.request_group_ids)
        self.assertEqual(
            self.session.encounter_ids,
            self.env["medical.encounter"].search(
                self.session.action_view_non_validated_encounters()["domain"]
            ),
        )
        non_validated = len(self.session.encounter_ids)
        self.assertEqual(
            non_validated, self.session.encounter_non_validated_count
        )
        self.session.refresh()
        self.assertEqual(len(self.session.invoice_ids), 0)
        self.assertFalse(self.session.down_payment_ids)
        for encounter in self.session.encounter_ids:
            self.assertEqual(
                non_validated, self.session.encounter_non_validated_count
            )
            encounter_aux = self.env["medical.encounter"].browse(
                self.session.open_validation_encounter(
                    encounter.internal_identifier
                )["res_id"]
            )
            action = self.session.action_view_non_validated_encounters()
            if non_validated > 1:
                self.assertIn(
                    encounter,
                    self.env["medical.encounter"].search(action["domain"]),
                )
            else:
                self.assertEqual(
                    encounter,
                    self.env["medical.encounter"].browse(action["res_id"]),
                )
            encounter_aux.with_context(
                from_barcode_reader=True
            ).admin_validate()
            encounter_aux.refresh()
            non_validated -= 1
            self.assertEqual(
                non_validated, self.session.encounter_non_validated_count
            )
            encounter_aux.sale_order_ids.refresh()
            self.assertTrue(
                encounter_aux.sale_order_ids.filtered(lambda r: r.invoice_ids)
            )
            self.assertTrue(
                encounter_aux.sale_order_ids.filtered(
                    lambda r: not r.invoice_ids
                )
            )
            self.assertTrue(
                all(
                    i.state != "draft"
                    for i in encounter_aux.mapped("sale_order_ids.invoice_ids")
                )
            )
            self.assertFalse(
                all(
                    line.invoice_lines
                    for line in encounter.mapped("sale_order_ids.order_line")
                )
            )

        self.assertEqual(0, self.session.encounter_non_validated_count)
        self.assertEqual(0, non_validated)
        self.assertEqual(0, self.session.encounter_non_validated_count)
        wzd = self.env["invoice.sales.by.group"].create(
            {
                "invoice_group_method_id": method_2.id,
                "customer_ids": [(4, self.payor.id)],
                "date_to": fields.Date.to_string(
                    fields.Date.from_string(fields.Date.today())
                    + relativedelta(days=1)
                ),
            }
        )
        wzd.invoice_sales_by_group()
        for encounter in self.session.encounter_ids:
            for sale_order in encounter.sale_order_ids:
                self.assertTrue(
                    all(line.invoice_lines for line in sale_order.order_line)
                )

    def test_validation(self):
        method = self.browse_ref("cb_medical_careplan_sale.by_preinvoicing")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.agreement_line3.authorization_method_id = self.method
        self.company.sale_merge_draft_invoice = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertTrue(group.procedure_request_ids)
        self.assertTrue(
            group.is_sellable_insurance or group.is_sellable_private
        )
        self.assertFalse(group.third_party_bill)
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertTrue(encounter.sale_order_ids)
        self.session.action_pos_session_close()
        self.pos_config.write({"session_sequence_prefix": "POS"})
        self.assertTrue(self.pos_config.session_sequence_id)
        self.assertEqual(
            self.pos_config.session_sequence_id.prefix, "POS/%(range_y)s/"
        )
        self.pos_config.write({"session_sequence_prefix": "PS"})
        self.assertTrue(self.pos_config.session_sequence_id)
        self.assertEqual(
            self.pos_config.session_sequence_id.prefix, "PS/%(range_y)s/"
        )
        self.pos_config.open_session_cb()
        self.assertTrue(self.session.request_group_ids)
        self.assertFalse(encounter.is_preinvoiced)
        line = encounter.sale_order_ids.order_line
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        encounter.toggle_is_preinvoiced()
        self.assertTrue(encounter.is_preinvoiced)
        self.coverage_template.write(
            {"subscriber_required": True, "subscriber_format": "^1.*$"}
        )
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        line.write({"subscriber_id": "23"})
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        line.write({"subscriber_id": "123"})
        self.agreement_line3.write(
            {
                "authorization_format_id": self.format.id,
                "authorization_method_id": self.method.id,
            }
        )
        action = (
            self.env["medical.request.group.check.authorization"]
            .with_context(line.check_authorization_action()["context"])
            .create({"authorization_number": "1234A"})
        )
        action.run()
        self.assertNotEqual(line.authorization_status, "authorized")
        self.assertEqual(line.authorization_number, "1234A")
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        action = (
            self.env["medical.request.group.check.authorization"]
            .with_context(line.check_authorization_action()["context"])
            .create({"authorization_number": "1234"})
        )
        action.run()
        self.assertEqual(line.authorization_status, "authorized")
        self.assertEqual(line.authorization_number, "1234")
        self.agreement_line3.write(
            {"authorization_format_id": self.format_letter.id}
        )
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        self.agreement_line3.write({"authorization_format_id": self.format.id})
        encounter.admin_validate()

    def test_patient_invoice(self):
        method = self.browse_ref("cb_medical_careplan_sale.by_patient")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.company.sale_merge_draft_invoice = True
        for _ in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private
            )
            self.assertFalse(group.third_party_bill)
            self.env["wizard.medical.encounter.close"].create(
                {
                    "encounter_id": encounter.id,
                    "pos_session_id": self.session.id,
                }
            ).run()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            for line in sale_order.order_line:
                self.assertFalse(line.agent_ids)
        self.session.action_pos_session_close()
        self.assertTrue(self.session.request_group_ids)
        self.assertEqual(
            self.session.encounter_ids,
            self.env["medical.encounter"].search(
                self.session.action_view_non_validated_encounters()["domain"]
            ),
        )
        non_validated = len(self.session.encounter_ids)
        action = self.session.open_validation_encounter(
            self.session.internal_identifier
        )
        self.assertEqual(action["res_model"], "barcode.action")
        for encounter in self.session.encounter_ids:
            self.assertEqual(
                non_validated, self.session.encounter_non_validated_count
            )
            encounter_aux = self.env["medical.encounter"].browse(
                self.session.open_validation_encounter(
                    encounter.internal_identifier
                )["res_id"]
            )
            action = self.session.action_view_non_validated_encounters()
            if non_validated > 1:
                self.assertIn(
                    encounter,
                    self.env["medical.encounter"].search(action["domain"]),
                )
            else:
                self.assertEqual(
                    encounter,
                    self.env["medical.encounter"].browse(action["res_id"]),
                )
            encounter_aux.admin_validate()
            non_validated -= 1
            self.assertEqual(
                non_validated, self.session.encounter_non_validated_count
            )
            for sale_order in encounter_aux.sale_order_ids:
                self.assertTrue(sale_order.invoice_ids)
                self.assertTrue(
                    all(i.state != "draft" for i in sale_order.invoice_ids)
                )
        self.assertEqual(0, non_validated)
        self.assertEqual(0, self.session.encounter_non_validated_count)

    def test_no_invoice(self):
        method = self.browse_ref("cb_medical_careplan_sale.no_invoice")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.company.sale_merge_draft_invoice = True
        sale_orders = self.env["sale.order"]
        for _ in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private
            )
            self.assertFalse(group.third_party_bill)
            self.env["wizard.medical.encounter.close"].create(
                {
                    "encounter_id": encounter.id,
                    "pos_session_id": self.session.id,
                }
            ).run()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            for line in sale_order.order_line:
                self.assertFalse(line.agent_ids)
            sale_orders |= sale_order
        self.session.action_pos_session_close()
        self.assertTrue(self.session.request_group_ids)
        for encounter in self.session.encounter_ids:
            encounter_aux = self.env["medical.encounter"].browse(
                self.session.open_validation_encounter(
                    encounter.internal_identifier
                )["res_id"]
            )
            encounter_aux.admin_validate()
        for line in sale_orders.mapped("order_line"):
            self.assertEqual(line.qty_to_invoice, 0)
        for encounter in self.session.encounter_ids:
            self.assertTrue(
                encounter.mapped("careplan_ids.procedure_request_ids")
            )
            for request in encounter.mapped(
                "careplan_ids.procedure_request_ids"
            ):
                request.draft2active()
                self.assertEqual(request.center_id, encounter.center_id)
                procedure = request.generate_event()
                procedure.performer_id = self.practitioner_01
                procedure.commission_agent_id = self.practitioner_01
                procedure.performer_id = self.practitioner_02
                procedure._onchange_performer_id()
                self.assertEqual(
                    procedure.commission_agent_id, self.practitioner_02
                )
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
        for encounter in self.session.encounter_ids:
            for request in encounter.careplan_ids.mapped(
                "procedure_request_ids"
            ):
                procedure = request.procedure_ids
                self.assertEqual(len(procedure.sale_agent_ids), 1)
                self.assertEqual(len(procedure.invoice_agent_ids), 0)
                procedure.performer_id = self.practitioner_01
                procedure.commission_agent_id = self.practitioner_01
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
        for _i in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private
            )
            self.assertFalse(group.third_party_bill)
            self.env["wizard.medical.encounter.close"].create(
                {
                    "encounter_id": encounter.id,
                    "pos_session_id": self.session.id,
                }
            ).run()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            for line in sale_order.order_line:
                self.assertFalse(line.agent_ids)
            sale_orders |= sale_order
        self.session.action_pos_session_close()
        self.assertTrue(self.session.request_group_ids)
        for encounter in self.session.encounter_ids:
            encounter_aux = self.env["medical.encounter"].browse(
                self.session.open_validation_encounter(
                    encounter.internal_identifier
                )["res_id"]
            )
            encounter_aux.admin_validate()
        action = (
            self.env["invoice.sales.by.group"]
            .create(
                {
                    "invoice_group_method_id": method.id,
                    "date_to": fields.Date.today() + relativedelta(days=-1),
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
                    "date_to": fields.Date.today() + relativedelta(days=1),
                    "company_ids": [(6, 0, self.company.ids)],
                }
            )
            .invoice_sales_by_group()
        )
        self.assertTrue(action.get("res_id", False))
        invoice = self.env["account.move"].browse(action.get("res_id", False))
        invoice.post()
        for line in invoice.invoice_line_ids:
            self.assertEqual(line.name, nomenclature_product.name)
        for sale_order in sale_orders:
            self.assertTrue(sale_order.invoice_status == "invoiced")
        for encounter in self.session.encounter_ids:
            for request in encounter.careplan_ids.mapped(
                "procedure_request_ids"
            ):
                request.draft2active()
                self.assertEqual(request.center_id, encounter.center_id)
                procedure = request.generate_event()
                procedure.performer_id = self.practitioner_01
                procedure.commission_agent_id = self.practitioner_01
                procedure.performer_id = self.practitioner_02
                procedure._onchange_performer_id()
                self.assertEqual(
                    procedure.commission_agent_id, self.practitioner_02
                )
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
        for encounter in self.session.encounter_ids:
            for request in encounter.careplan_ids.mapped(
                "procedure_request_ids"
            ):
                procedure = request.procedure_ids
                self.assertEqual(len(procedure.sale_agent_ids), 1)
                self.assertEqual(len(procedure.invoice_agent_ids), 1)
                procedure.performer_id = self.practitioner_01
                procedure.commission_agent_id = self.practitioner_01
                procedure.check_commission()
                self.assertEqual(len(procedure.sale_agent_ids), 1)
                self.assertEqual(len(procedure.invoice_agent_ids), 3)

    def test_preinvoice_no_invoice(self):
        method = self.browse_ref(
            "cb_medical_careplan_sale.no_invoice_preinvoice"
        )
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.company.sale_merge_draft_invoice = True
        sale_orders = self.env["sale.order"]
        for _i in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private
            )
            self.assertFalse(group.third_party_bill)
            self.env["wizard.medical.encounter.close"].create(
                {
                    "encounter_id": encounter.id,
                    "pos_session_id": self.session.id,
                }
            ).run()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            for line in sale_order.order_line:
                self.assertFalse(line.agent_ids)
            sale_orders |= sale_order
        self.session.action_pos_session_close()
        self.assertTrue(self.session.request_group_ids)
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
        for encounter in self.session.encounter_ids:
            encounter_aux = self.env["medical.encounter"].browse(
                self.session.open_validation_encounter(
                    encounter.internal_identifier
                )["res_id"]
            )
            with self.assertRaises(ValidationError):
                encounter_aux.admin_validate()
            encounter.toggle_is_preinvoiced()
            encounter_aux.admin_validate()
            self.assertTrue(
                encounter.sale_order_ids.filtered(
                    lambda r: r.preinvoice_status == "to preinvoice"
                    and any(
                        line.invoice_group_method_id == method
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
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            barcode = self.env["wizard.sale.preinvoice.group.barcode"].create(
                {"preinvoice_group_id": preinvoice.id}
            )
            for encounter in self.session.encounter_ids:
                barcode.on_barcode_scanned(encounter.internal_identifier)
                self.assertEqual(barcode.status_state, 0)
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertFalse(preinvoice.move_id)
        invoices = invoice_obj.search(
            [("partner_id", "in", [self.payor.id, self.sub_payor.id])]
        )
        self.assertFalse(invoices)

    def close_encounter(self, encounter):
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        if encounter.state == "finished":
            return
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "payment_method_id": self.session.payment_method_ids.ids[0],
            }
        ).run()

    def test_validation_constrain(self):
        self.plan_definition2.write({"third_party_bill": False})
        self.agreement_line3.write({"coverage_percentage": 0})
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.close_encounter(encounter)
        self.session.action_pos_session_closing_control()
        self.session.action_pos_session_approve()
        self.assertEqual(self.session.validation_status, "in_progress")
        with self.assertRaises(UserError):
            encounter.sale_order_ids.mapped("order_line").medical_cancel(
                self.cancel_reason
            )

    def test_cancel_service(self):
        self.plan_definition2.write({"third_party_bill": False})
        self.agreement_line3.write({"coverage_percentage": 100})
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.close_encounter(encounter)
        self.session.action_pos_session_closing_control()
        self.session.action_pos_session_approve()
        encounter.sale_order_ids.mapped("order_line").medical_cancel(
            self.cancel_reason
        )
        self.assertFalse(encounter.sale_order_ids.mapped("order_line"))

    def test_validation_no_invoices(self):
        self.session.action_pos_session_close()
        self.assertEqual(self.session.validation_status, "finished")

    def test_validation_add_service(self):
        self.plan_definition2.write({"third_party_bill": False})
        self.agreement_line3.write({"coverage_percentage": 100})
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(encounter.careplan_ids, careplan)
        self.agreement.write(
            {"coverage_template_ids": [(4, self.coverage_template_2.id)]}
        )
        self.env["medical.encounter.validation.add.service"].create(
            {
                "encounter_id": encounter.id,
                "action_type": "new",
                "coverage_template_id": self.coverage_template_2.id,
                "payor_id": self.payor.id,
                "agreement_line_id": self.agreement_line3.id,
            }
        ).run()
        self.assertEqual(2, len(encounter.careplan_ids))
