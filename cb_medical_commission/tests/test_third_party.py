from odoo.addons.cb_medical_careplan_sale.tests import common
from odoo.exceptions import UserError


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
        cls.def_third_party_product = cls.create_product("THIRD PARTY PRODUCT")
        cls.env["ir.config_parameter"].set_param(
            "cb.default_third_party_product", cls.def_third_party_product.id
        )

    def test_performer(self):
        self.plan_definition2.write(
            {"third_party_bill": False, "performer_required": True}
        )
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity5.id,
                "direct_plan_definition_id": self.plan_definition2.id,
                "is_billable": False,
                "name": "Action",
                "performer_id": self.practitioner_02.id,
            }
        )
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
        self.assertEqual(careplan.center_id, encounter.center_id)
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line3.id,
                "performer_id": self.practitioner_01.id,
            }
        )
        self.assertIn(self.agreement, wizard.agreement_ids)
        self.action.is_billable = False
        wizard.run()
        group = self.env["medical.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        group.ensure_one()
        group.refresh()
        self.assertEqual(group.center_id, encounter.center_id)
        self.assertEqual(group.performer_id, self.practitioner_01)
        self.assertEqual(len(group.procedure_request_ids.ids), 2)
        self.assertTrue(
            group.procedure_request_ids.filtered(
                lambda r: r.performer_id == self.practitioner_01
            )
        )
        self.assertTrue(
            group.procedure_request_ids.filtered(
                lambda r: r.performer_id == self.practitioner_02
            )
        )

    def test_third_party(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(encounter.sale_order_count, 0)
        self.assertTrue(group.procedure_request_ids)
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_02
        self.practitioner_02.third_party_sequence_id = self.env[
            "ir.sequence"
        ].create({"name": "sequence"})
        self.assertTrue(
            group.is_sellable_insurance or group.is_sellable_private
        )
        self.assertTrue(group.third_party_bill)
        encounter.create_sale_order()
        self.assertGreater(encounter.sale_order_count, 0)
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertTrue(sale_order.third_party_order)
        self.assertEqual(
            sale_order.third_party_partner_id, self.practitioner_02
        )
        self.assertTrue(
            sale_order.third_party_partner_id, self.practitioner_02
        )
        encounter.sale_order_ids.action_confirm()
        with self.assertRaises(UserError):
            encounter.sale_order_ids.with_context(
                active_model=encounter.sale_order_ids._name
            )._create_invoices()

    def test_preinvoice_third_party(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(encounter.sale_order_count, 0)
        self.assertTrue(group.procedure_request_ids)
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_02
        self.practitioner_02.third_party_sequence_id = self.env[
            "ir.sequence"
        ].create({"name": "sequence"})
        self.assertTrue(
            group.is_sellable_insurance or group.is_sellable_private
        )
        self.assertTrue(group.third_party_bill)
        encounter.create_sale_order()
        self.assertGreater(encounter.sale_order_count, 0)
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertTrue(sale_order.third_party_order)
        self.assertEqual(
            sale_order.third_party_partner_id, self.practitioner_02
        )
        self.assertTrue(
            sale_order.third_party_partner_id, self.practitioner_02
        )
        encounter.sale_order_ids.action_confirm()
        self.assertTrue(encounter.sale_order_ids.third_party_order_ids)
        encounter.sale_order_ids.third_party_order_ids.action_confirm()

        for line in encounter.sale_order_ids.third_party_order_ids.order_line:
            line.qty_delivered = line.product_uom_qty
        preinvoice_obj = self.env["sale.preinvoice.group"]
        self.assertFalse(
            preinvoice_obj.search(
                [("partner_id", "=", self.practitioner_02.id)]
            )
        )
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.practitioner_02.ids)],
            }
        ).run()
        self.assertTrue(
            preinvoice_obj.search(
                [("partner_id", "=", self.practitioner_02.id)]
            )
        )
        preinvoices = preinvoice_obj.search(
            [
                ("partner_id", "=", self.practitioner_02.id),
                ("state", "=", "draft"),
            ]
        )
        self.assertTrue(preinvoices)
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            result = preinvoice.scan_barcode_preinvoice(
                encounter.internal_identifier
            )
            self.assertEqual(result["context"]["default_state"], "waiting")
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.move_id)
        move = preinvoices.mapped("move_id")
        self.assertTrue(move)
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(encounter.sale_order_count, 0)
        self.assertTrue(group.procedure_request_ids)
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_02
        self.assertTrue(
            group.is_sellable_insurance or group.is_sellable_private
        )
        self.assertTrue(group.third_party_bill)
        encounter.create_sale_order()
        self.assertGreater(encounter.sale_order_count, 0)
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertTrue(sale_order.third_party_order)
        self.assertEqual(
            sale_order.third_party_partner_id, self.practitioner_02
        )
        self.assertTrue(
            sale_order.third_party_partner_id, self.practitioner_02
        )
        encounter.sale_order_ids.action_confirm()
        encounter.sale_order_ids.third_party_order_ids.action_confirm()
        for line in encounter.sale_order_ids.third_party_order_ids.order_line:
            line.qty_delivered = line.product_uom_qty
        preinvoice_obj = self.env["sale.preinvoice.group"]
        self.assertFalse(
            preinvoice_obj.search(
                [
                    ("partner_id", "=", self.practitioner_02.id),
                    ("state", "=", "draft"),
                ]
            )
        )
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.practitioner_02.ids)],
            }
        ).run()
        self.assertTrue(
            preinvoice_obj.search(
                [("partner_id", "=", self.practitioner_02.id)]
            )
        )
        preinvoices = preinvoice_obj.search(
            [
                ("partner_id", "=", self.practitioner_02.id),
                ("state", "=", "draft"),
            ]
        )
        self.assertTrue(preinvoices)
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            result = preinvoice.scan_barcode_preinvoice(
                encounter.internal_identifier
            )
            self.assertEqual(result["context"]["default_state"], "waiting")
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.move_id)
            self.assertEqual(move, preinvoice.move_id)
