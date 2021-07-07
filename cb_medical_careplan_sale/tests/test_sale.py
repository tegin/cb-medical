# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import ValidationError

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
        encounter.create_sale_order()
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
        encounter.careplan_ids.refresh()
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
