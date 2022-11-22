# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import SavepointCase


class MedicalSavePointCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        self = cls
        name = "testing_remote_server"
        self.remote = self.env["res.remote"].search([("name", "=", name)])
        if not self.remote:
            self.remote = self.env["res.remote"].create(
                {"name": name, "ip": "127.0.0.1", "in_network": True}
            )
        self.nomenclature = self.env["product.nomenclature"].create(
            {"name": "Nomenclature", "code": "nomenc"}
        )
        self.payor = self.env["res.partner"].create(
            {
                "name": "Payor",
                "is_payor": True,
                "is_medical": True,
                "invoice_nomenclature_id": self.nomenclature.id,
            }
        )
        self.sub_payor = self.env["res.partner"].create(
            {
                "name": "Sub Payor",
                "is_sub_payor": True,
                "is_medical": True,
                "payor_id": self.payor.id,
            }
        )
        self.coverage_template = self.env["medical.coverage.template"].create(
            {"payor_id": self.payor.id, "name": "Coverage"}
        )
        self.coverage_template_2 = self.env["medical.coverage.template"].create(
            {"payor_id": self.payor.id, "name": "Coverage 2"}
        )
        self.company = self.env.ref("base.main_company")
        for order in self.env["sale.order"].search(
            [
                ("company_id", "=", self.company.id),
                ("state", "!=", "cancel"),
                ("invoice_status", "!=", "invoiced"),
            ]
        ):
            # We cancel all demo orders just in case
            order.action_cancel()
        self.company.third_party_journal_id = self.env["account.journal"].create(
            {
                "name": "Journal",
                "code": "THIRD",
                "company_id": self.company.id,
                "type": "general",
            }
        )
        self.customer_acc = self.env["account.account"].create(
            {
                "company_id": self.company.id,
                "code": "ThirdPartyCust",
                "name": "Third party customer account",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.supplier_acc = self.env["account.account"].create(
            {
                "company_id": self.company.id,
                "code": "ThirdPartySupp",
                "name": "Third party supplier account",
                "user_type_id": self.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        self.company.write(
            {
                "default_third_party_customer_account_id": self.customer_acc.id,
                "default_third_party_supplier_account_id": self.supplier_acc.id,
            }
        )
        self.tax = self.env["account.tax"].create(
            {
                "name": "TAX",
                "amount_type": "percent",
                "amount": 0,
                "type_tax_use": "sale",
                "company_id": self.company.id,
            }
        )
        self.center = self.env["res.partner"].create(
            {
                "name": "Center",
                "is_medical": True,
                "is_center": True,
                "encounter_sequence_prefix": "S",
            }
        )
        self.location = self.env["res.partner"].create(
            {
                "name": "Location",
                "is_medical": True,
                "is_location": True,
                "center_id": self.center.id,
                "stock_location_id": self.env.ref("stock.warehouse0").lot_stock_id.id,
                "stock_picking_type_id": self.env["stock.picking.type"]
                .search([], limit=1)
                .id,
            }
        )
        self.document_type = self.env["medical.document.type"].create(
            {
                "name": "CI",
                "document_type": "action",
                "report_action_id": self.env.ref(
                    "medical_document.action_report_document_report_base"
                ).id,
            }
        )
        self.lang_es = self.env.ref("base.lang_es")
        if not self.lang_es.active:
            self.lang_es.active = True
        self.lang_en = self.env.ref("base.lang_en")
        if not self.lang_en.active:
            self.lang_en.active = True
        self.env["medical.document.type.lang"].create(
            {
                "lang": self.lang_es.code,
                "document_type_id": self.document_type.id,
                "text": "<p>%s</p><p>${object.patient_id.name}"
                "</p>" % self.lang_es.code,
            }
        )
        self.env["medical.document.type.lang"].create(
            {
                "lang": self.lang_en.code,
                "document_type_id": self.document_type.id,
                "text": "<p>%s</p><p>${object.patient_id.name}"
                "</p>" % self.lang_en.code,
            }
        )
        self.document_type.draft2current()
        self.agreement = self.env["medical.coverage.agreement"].create(
            {
                "name": "Agreement",
                "center_ids": [(4, self.center.id)],
                "coverage_template_ids": [(4, self.coverage_template.id)],
                "company_id": self.company.id,
                "invoice_group_method_id": self.env.ref(
                    "cb_medical_careplan_sale.by_preinvoicing"
                ).id,
                "authorization_method_id": self.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.format = self.env["medical.authorization.format"].create(
            {"code": "TEST", "name": "test", "authorization_format": "^1.*$"}
        )
        self.patient_01 = self.create_patient("Patient 01")
        self.coverage_01 = self.env["medical.coverage"].create(
            {
                "patient_id": self.patient_01.id,
                "coverage_template_id": self.coverage_template.id,
            }
        )
        self.coverage_02 = self.env["medical.coverage"].create(
            {
                "patient_id": self.patient_01.id,
                "coverage_template_id": self.coverage_template_2.id,
            }
        )
        self.product_01 = self.create_product("Medical resonance")
        self.product_02 = self.create_product("Report")
        self.product_04 = self.create_product("Report 04")
        self.product_05 = self.create_product("Report 05")
        self.product_06 = self.create_product("Document 06")
        self.product_07 = self.create_product("Document 07")
        self.service = self.env["product.product"].create(
            {
                "name": "Service",
                "type": "service",
                "taxes_id": [(6, 0, self.tax.ids)],
            }
        )
        self.category = self.env["product.category"].create({"name": "Category"})
        self.product_03 = self.env["product.product"].create(
            {
                "type": "consu",
                "categ_id": self.category.id,
                "name": "Clinical material",
                "is_medication": True,
                "lst_price": 10.0,
                "taxes_id": [(6, 0, self.tax.ids)],
            }
        )
        self.product_03.qty_available = 50.0
        self.product_04 = self.create_product("Medical visit")
        self.product_05 = self.create_product("Extra product")
        self.lab_product = self.create_product("Laboratory Product")
        self.type = self.env.ref("medical_workflow.medical_workflow")
        self.type.model_ids = [
            (
                4,
                self.env.ref(
                    "medical_medication_request.model_medical_medication_request"
                ).id,
            )
        ]
        self.plan_definition = self.env["workflow.plan.definition"].create(
            {"name": "Plan", "type_id": self.type.id, "is_billable": True}
        )
        self.plan_definition.activate()
        self.plan_definition2 = self.env["workflow.plan.definition"].create(
            {
                "name": "Plan2",
                "type_id": self.type.id,
                "is_billable": True,
                "is_breakdown": False,
                "third_party_bill": True,
            }
        )
        self.plan_definition2.activate()
        self.plan_definition3 = self.env["workflow.plan.definition"].create(
            {
                "name": "Plan2",
                "type_id": self.type.id,
                "is_billable": True,
                "is_breakdown": False,
                "third_party_bill": False,
            }
        )
        self.plan_definition3.activate()
        self.activity = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity",
                "service_id": self.product_02.id,
                "model_id": self.env.ref(
                    "medical_clinical_procedure." "model_medical_procedure_request"
                ).id,
                "type_id": self.type.id,
            }
        )
        self.activity.activate()
        self.activity2 = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity2",
                "service_id": self.service.id,
                "model_id": self.env.ref(
                    "medical_medication_request." "model_medical_medication_request"
                ).id,
                "type_id": self.type.id,
            }
        )
        self.activity2.activate()
        self.activity3 = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity3",
                "service_id": self.product_05.id,
                "model_id": self.env.ref(
                    "medical_document.model_medical_document_reference"
                ).id,
                "document_type_id": self.document_type.id,
                "type_id": self.type.id,
            }
        )
        self.activity3.activate()
        self.activity4 = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity4",
                "service_id": self.product_06.id,
                "model_id": self.env.ref(
                    "medical_document.model_medical_document_reference"
                ).id,
                "document_type_id": self.document_type.id,
                "type_id": self.type.id,
            }
        )
        self.activity4.activate()
        self.activity5 = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity 5",
                "service_id": self.product_04.id,
                "model_id": self.env.ref(
                    "medical_clinical_procedure." "model_medical_procedure_request"
                ).id,
                "type_id": self.type.id,
            }
        )
        self.activity5.activate()
        self.lab_activity = self.env["workflow.activity.definition"].create(
            {
                "name": "Laboratory activity",
                "service_id": self.product_07.id,
                "model_id": self.env.ref(
                    "medical_clinical_laboratory." "model_medical_laboratory_request"
                ).id,
                "type_id": self.type.id,
            }
        )
        self.lab_activity.activate()
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity.id,
                "direct_plan_definition_id": self.plan_definition2.id,
                "is_billable": False,
                "name": "Action",
            }
        )
        self.action = self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": True,
                "name": "Action",
            }
        )
        self.action2 = self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity2.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": True,
                "name": "Action2",
            }
        )
        self.action3 = self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity3.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": False,
                "name": "Action3",
            }
        )
        self.action4 = self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity4.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": False,
                "name": "Action4",
            }
        )
        self.agreement_line = self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.product_01.id,
                "coverage_agreement_id": self.agreement.id,
                "plan_definition_id": self.plan_definition.id,
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
        self.method = self.env.ref("medical_financial_coverage_request.only_number")
        self.format = self.env["medical.authorization.format"].create(
            {
                "name": "Number",
                "code": "testing_number",
                "always_authorized": False,
                "authorization_format": "^[0-9]*$",
            }
        )
        self.format_letter = self.env["medical.authorization.format"].create(
            {
                "name": "Number",
                "code": "testing_number",
                "always_authorized": False,
                "authorization_format": "^[a-zA-Z]*$",
            }
        )
        self.agreement_line2 = self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.service.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 0.0,
                "coverage_percentage": 100.0,
                "authorization_method_id": self.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.agreement_line3 = self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.product_04.id,
                "coverage_agreement_id": self.agreement.id,
                "plan_definition_id": self.plan_definition2.id,
                "total_price": 100.0,
                "coverage_percentage": 0.0,
                "authorization_method_id": self.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.lab_agreement_line = self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.lab_product.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 0.0,
                "coverage_percentage": 0.0,
                "authorization_method_id": self.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.practitioner_01 = self.create_practitioner("Practitioner 01")
        self.practitioner_02 = self.create_practitioner("Practitioner 02")
        self.product_01.medical_commission = True
        self.action.fixed_fee = 1

        self.sb_account = self.env["account.account"].create(
            {
                "name": "Safe box account",
                "code": "5720SBC",
                "company_id": self.company.id,
                "currency_id": self.company.currency_id.id,
                "user_type_id": self.env.ref("account.data_account_type_liquidity").id,
            }
        )
        self.bank_account = self.env["account.account"].create(
            {
                "name": "Bank account",
                "code": "5720BNK",
                "company_id": self.company.id,
                "currency_id": self.company.currency_id.id,
                "user_type_id": self.env.ref("account.data_account_type_liquidity").id,
            }
        )
        self.cash_account = self.env["account.account"].create(
            {
                "name": "Safe box account",
                "code": "572CSH",
                "company_id": self.company.id,
                "currency_id": self.company.currency_id.id,
                "user_type_id": self.env.ref("account.data_account_type_liquidity").id,
            }
        )
        self.reina = self.env["res.partner"].create(
            {
                "name": "Reina",
                "is_medical": True,
                "is_center": True,
                "encounter_sequence_prefix": "9",
            }
        )
        param_obj = self.env["ir.config_parameter"].sudo()
        param = param_obj.get_param("sale.default_deposit_product_id", False)
        if not param:
            param_obj.set_param(
                "sale.default_deposit_product_id",
                self.create_product("Down payment").id,
            )
        self.discount = self.env["medical.sale.discount"].create(
            {"name": "Discount 01", "percentage": 50}
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Product",
                "type": "consu",
                # We don't want to check if there is enough material
                "categ_id": self.category.id,
            }
        )

    @classmethod
    def create_patient(cls, name):
        return cls.env["medical.patient"].create({"name": name})

    @classmethod
    def create_product(cls, name):
        return cls.env["product.product"].create(
            {
                "type": "service",
                "name": name,
                "taxes_id": [(6, 0, cls.tax.ids)],
            }
        )

    def create_careplan_and_group(self, agreement_line, coverage=False):
        if not coverage:
            coverage = self.coverage_01
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        careplan_wizard = (
            self.env["medical.encounter.add.careplan"]
            .with_context(default_encounter_id=encounter.id)
            .new({"coverage_id": coverage.id})
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
        self.assertEqual(careplan.center_id, encounter.center_id)
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": agreement_line.id,
            }
        )
        self.assertIn(self.agreement, wizard.agreement_ids)
        self.action.is_billable = False
        wizard.run()
        group = self.env["medical.request.group"].search(
            [
                ("careplan_id", "=", careplan.id),
                ("service_id", "=", agreement_line.product_id.id),
            ]
        )
        group.ensure_one()
        group.refresh()
        self.assertEqual(group.center_id, encounter.center_id)
        return encounter, careplan, group

    @classmethod
    def create_practitioner(cls, name):
        return cls.env["res.partner"].create({"name": name, "is_practitioner": True})
