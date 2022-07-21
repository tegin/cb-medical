# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from mock import patch
from odoo.exceptions import ValidationError
from odoo.tests.common import Form

from ..tests import common


class TestCBSale(common.MedicalSavePointCase):
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
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line.id,
            }
        )
        with self.assertRaises(ValidationError):
            wizard.run()

    def test_invoice_multiple_coverage_template(self):
        method = self.browse_ref("cb_medical_careplan_sale.by_customer")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.agreement.write(
            {"coverage_template_ids": [(4, self.coverage_template_2.id)]}
        )
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        encounter.create_sale_order()
        self.assertTrue(encounter.sale_order_ids)
        encounter_02, careplan_02, group_02 = self.create_careplan_and_group(
            self.agreement_line3, coverage=self.coverage_02
        )
        encounter_02.create_sale_order()
        self.assertTrue(encounter_02.sale_order_ids)
        sale_orders = encounter.sale_order_ids | encounter_02.sale_order_ids
        sale_orders.action_confirm()
        invoices = sale_orders.with_context(
            active_model=sale_orders._name
        )._create_invoices()
        self.assertEqual(2, len(invoices))
        self.assertEqual(invoices.mapped("partner_id"), self.payor)

    def test_invoice_single_coverage_template(self):
        method = self.browse_ref("cb_medical_careplan_sale.by_customer")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.agreement.write(
            {"coverage_template_ids": [(4, self.coverage_template_2.id)]}
        )
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        encounter.create_sale_order()
        self.assertTrue(encounter.sale_order_ids)
        encounter_02, careplan_02, group_02 = self.create_careplan_and_group(
            self.agreement_line3
        )
        encounter_02.create_sale_order()
        self.assertTrue(encounter_02.sale_order_ids)
        sale_orders = encounter.sale_order_ids | encounter_02.sale_order_ids
        sale_orders.action_confirm()
        invoices = sale_orders.with_context(
            active_model=sale_orders._name
        )._create_invoices()
        self.assertEqual(1, len(invoices))
        self.assertEqual(invoices.mapped("partner_id"), self.payor)

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

    def test_discount(self):
        method = self.browse_ref("cb_medical_careplan_sale.no_invoice")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
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
        self.assertFalse(group.sale_order_line_ids)
        self.assertEqual(group.sale_order_line_count, 0)
        self.assertEqual(encounter.sale_order_count, 0)
        self.assertEqual(encounter.invoice_count, 0)
        encounter.create_sale_order()
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertEqual(encounter.sale_order_count, 1)
        group.refresh()
        self.assertTrue(group.sale_order_line_ids)
        self.assertEqual(group.sale_order_line_count, 1)
        self.assertEqual(sale_order.patient_name, "Patient 01")
        self.assertEqual(sale_order.order_line.patient_name, "Patient 01")
        self.assertEqual(sale_order.amount_total, 50)
        self.assertEqual(sale_order.order_line.discount, 50)
        sale_order.patient_name = "OTHER NAME"
        sale_order.flush()
        self.assertEqual(sale_order.order_line.patient_name, "OTHER NAME")
        sale_order.order_line.patient_name = "Patient 01"
        sale_order.order_line.flush()
        self.assertEqual(sale_order.patient_name, "Patient 01")
        self.assertEqual(encounter.invoice_count, 0)
        sale_order.action_confirm()
        sale_order.with_context(
            active_model=sale_order._name
        )._create_invoices()
        self.assertEqual(encounter.invoice_count, 1)
        action = encounter.action_view_invoice()
        self.assertEqual(
            self.env[action["res_model"]].browse(action["res_id"]),
            sale_order.invoice_ids,
        )
        invoice = sale_order.invoice_ids
        self.assertEqual(invoice.amount_total, 50)
        self.assertEqual(invoice.invoice_line_ids.discount, 50)

    def test_agreement_discount(self):
        method = self.browse_ref("cb_medical_careplan_sale.no_invoice")
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.agreement.discount = 50
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertFalse(group.medical_sale_discount_id)
        encounter.create_sale_order()
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertEqual(encounter.sale_order_count, 1)
        group.refresh()
        self.assertTrue(group.sale_order_line_ids)
        self.assertEqual(group.sale_order_line_count, 1)
        self.assertEqual(sale_order.amount_total, 100)
        self.assertEqual(sale_order.order_line.discount, 0)
        sale_order.action_confirm()
        sale_order.with_context(
            active_model=sale_order._name
        )._create_invoices()
        self.assertEqual(encounter.invoice_count, 1)
        action = encounter.action_view_invoice()
        self.assertEqual(
            self.env[action["res_model"]].browse(action["res_id"]),
            sale_order.invoice_ids,
        )
        invoice = sale_order.invoice_ids
        self.assertEqual(invoice.invoice_line_ids.discount, 50)
        self.assertEqual(invoice.amount_total, 50)

    def test_careplan_add_function_01(self):
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
        encounter.careplan_ids.refresh()
        self.assertTrue(encounter.careplan_ids.request_group_ids)

    def test_careplan_add_function_02(self):
        encounter_action = self.env["medical.encounter"].create_encounter(
            patient=self.patient_01.id,
            center=self.center.id,
            careplan_data=[
                {
                    "payor": self.payor.id,
                    "coverage_template": self.coverage_template.id,
                    "service": self.agreement_line3.product_id,
                }
            ],
        )
        encounter = self.env["medical.encounter"].browse(
            encounter_action["res_id"]
        )
        self.assertTrue(encounter)
        self.assertTrue(encounter.careplan_ids)
        encounter.careplan_ids.refresh()
        self.assertTrue(encounter.careplan_ids.request_group_ids)

    def test_careplan_add_function_sub_payor(self):
        encounter_action = self.env["medical.encounter"].create_encounter(
            patient=self.patient_01.id,
            center=self.center.id,
            careplan_data=[
                {
                    "payor": self.payor.id,
                    "coverage_template": self.coverage_template.id,
                    "sub_payor": self.sub_payor.id,
                    "service": self.agreement_line3.product_id,
                }
            ],
        )
        encounter = self.env["medical.encounter"].browse(
            encounter_action["res_id"]
        )
        self.assertTrue(encounter)
        self.assertTrue(encounter.careplan_ids)
        encounter.careplan_ids.refresh()
        self.assertEqual(encounter.careplan_ids.sub_payor_id, self.sub_payor)
        self.assertEqual(
            encounter.careplan_ids.request_group_ids.sub_payor_id,
            self.sub_payor,
        )

    def test_careplan_add_function_performer(self):
        self.plan_definition2.performer_required = True
        encounter_action = self.env["medical.encounter"].create_encounter(
            patient=self.patient_01.id,
            center=self.center.id,
            careplan_data=[
                {
                    "payor": self.payor.id,
                    "coverage_template": self.coverage_template.id,
                    "sub_payor": self.sub_payor.id,
                    "service": self.agreement_line3.product_id,
                    "order_by": self.practitioner_01.id,
                    "performer": self.practitioner_02.id,
                }
            ],
        )
        encounter = self.env["medical.encounter"].browse(
            encounter_action["res_id"]
        )
        self.assertTrue(encounter)
        self.assertTrue(encounter.careplan_ids)
        encounter.careplan_ids.refresh()
        self.assertEqual(encounter.careplan_ids.sub_payor_id, self.sub_payor)
        self.assertEqual(
            encounter.careplan_ids.request_group_ids.order_by_id,
            self.practitioner_01,
        )
        self.assertEqual(
            encounter.careplan_ids.request_group_ids.performer_id,
            self.practitioner_02,
        )

    def test_careplan_raises_01(self):
        self.coverage_01.patient_id = self.create_patient("ANOTHER PATIENT")
        with self.assertRaises(ValidationError):
            self.env["medical.encounter"].create_encounter(
                patient=self.patient_01.id,
                center=self.center.id,
                careplan_data=[
                    {
                        "coverage": self.coverage_01,
                        "service": self.agreement_line3.product_id.id,
                    }
                ],
            )

    def test_careplan_raises_02(self):
        with self.assertRaises(ValidationError):
            self.env["medical.encounter"].create_encounter(
                patient=self.patient_01.id,
                center=self.center.id,
                careplan_data=[
                    {"service": self.agreement_line3.product_id.id}
                ],
            )

    def test_careplan_raises_03(self):
        with self.assertRaises(ValidationError):
            self.env["medical.encounter"].create_encounter(
                patient=self.patient_01.id,
                center=self.center.id,
                careplan_data=[
                    {
                        "payor": self.payor,
                        "service": self.agreement_line3.product_id.id,
                    }
                ],
            )

    def test_careplan_raises_04(self):
        with self.assertRaises(ValidationError):
            self.env["medical.encounter"].create_encounter(
                patient=self.patient_01.id,
                center=self.center.id,
                careplan_data=[
                    {
                        "payor": self.payor,
                        "coverage_template": self.coverage_template,
                    }
                ],
            )

    def test_careplan_add_function_breakdown_raises_01(self):
        self.plan_definition2.third_party_bill = False
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
        encounter.careplan_ids.refresh()
        with self.assertRaises(ValidationError):
            encounter.careplan_ids.request_group_ids.breakdown()

    def test_careplan_add_function_breakdown_raises_02(self):
        self.plan_definition2.third_party_bill = False
        self.plan_definition2.is_breakdown = True
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
        encounter.create_sale_order()
        encounter.careplan_ids.refresh()
        with self.assertRaises(ValidationError):
            encounter.careplan_ids.request_group_ids.breakdown()

    def test_careplan_add_function_breakdown_raises_03(self):
        self.plan_definition2.third_party_bill = False
        self.plan_definition2.is_breakdown = True
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
        encounter.careplan_ids.refresh()
        with self.assertRaises(ValidationError):
            encounter.careplan_ids.request_group_ids.breakdown()

    def test_careplan_add_function_breakdown(self):
        self.plan_definition2.third_party_bill = False
        self.plan_definition2.is_breakdown = True
        self.agreement_line = self.env[
            "medical.coverage.agreement.item"
        ].create(
            {
                "product_id": self.product_02.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 100,
                "coverage_percentage": 50,
                "authorization_method_id": self.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
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
        encounter.careplan_ids.refresh()
        encounter.careplan_ids.request_group_ids.breakdown()

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

    def test_sale_laboratory_no_parameter(self):
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.lab_activity.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": False,
                "name": "Action4",
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
        event = (
            self.env["medical.laboratory.sample"]
            .search([("encounter_id", "=", encounter.id)])
            .generate_event(
                {
                    "service_id": self.laboratory_parameter.id,
                    "performer_id": self.practitioner_01.id,
                }
            )
        )
        event.flush()
        with self.assertRaises(ValidationError):
            event.laboratory_request_id = lab_req

    def test_sale_laboratory(self):
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.lab_activity.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": False,
                "name": "Action4",
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
        self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.laboratory_parameter.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 20.0,
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
        encounter.refresh()
        event = (
            self.env["medical.laboratory.sample"]
            .search([("encounter_id", "=", encounter.id)])
            .generate_event(
                {
                    "service_id": self.laboratory_parameter.id,
                    "performer_id": self.practitioner_01.id,
                }
            )
        )
        event.flush()
        self.assertEqual(
            event.laboratory_request_id, encounter.laboratory_request_ids
        )
        encounter.create_sale_order()
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
        self.assertEqual(encounter.invoice_count, 0)
        sale_orders = encounter.sale_order_ids
        for sale_order in sale_orders:
            sale_order.action_confirm()
            sale_order.with_context(
                active_model=sale_order._name
            )._create_invoices()
        self.assertEqual(encounter.invoice_count, 2)

    def test_add_careplan_form(self):
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        payor = self.env["res.partner"].create(
            {
                "name": "Payor",
                "is_payor": True,
                "is_medical": True,
                "invoice_nomenclature_id": self.nomenclature.id,
            }
        )
        careplan_wizard = Form(
            self.env["medical.encounter.add.careplan"].with_context(
                default_encounter_id=encounter.id
            )
        )
        careplan_wizard.coverage_id = self.coverage_01
        self.assertEqual(careplan_wizard.payor_id, self.payor)
        self.assertEqual(
            careplan_wizard.coverage_template_id, self.coverage_template
        )
        careplan_wizard.coverage_template_id = self.coverage_template_2
        self.assertFalse(careplan_wizard.coverage_id)
        careplan_wizard.sub_payor_id = self.sub_payor
        self.assertTrue(careplan_wizard.coverage_template_id)
        careplan_wizard.payor_id = payor
        self.assertFalse(careplan_wizard.coverage_template_id)
        self.assertFalse(careplan_wizard.sub_payor_id)

    @patch(
        "odoo.addons.base_report_to_printer.models.printing_printer."
        "PrintingPrinter.print_file"
    )
    def test_document(self, mock):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.patient_01.lang = self.lang_en.code
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(careplan.document_reference_ids)
        self.assertTrue(group.document_reference_ids)
        action = group.with_context(
            model_name="medical.document.reference"
        ).action_view_request()
        self.assertEqual(
            self.env[action["res_model"]].search(action["domain"]),
            group.document_reference_ids,
        )
        documents = group.document_reference_ids.filtered(
            lambda r: r.document_type == "action"
        )
        self.assertTrue(documents)
        for document in documents:
            document.view()
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.product_02.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 110,
                "coverage_percentage": 0.5,
                "authorization_method_id": self.browse_ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        group.breakdown()
        self.assertFalse(group.is_billable)
        self.assertFalse(group.is_breakdown)
