from odoo.tests.common import Form

from odoo.addons.cb_medical_pos.tests import common


class TestCBMedicalCommission(common.MedicalSavePointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category.write({"category_product_id": cls.service.id})
        cls.product_extra = cls.env["product.product"].create(
            {
                "type": "consu",
                "categ_id": cls.category.id,
                "name": "Clinical material",
                "is_medication": True,
                "lst_price": 10.0,
                "taxes_id": [(6, 0, cls.tax.ids)],
            }
        )

    def test_careplan_sale_medication(self):
        self.action.is_billable = False
        encounter, careplan, group = self.create_careplan_and_group(self.agreement_line)
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
            groups.filtered(lambda r: r.child_model == "medical.medication.request")
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
        self.assertFalse(encounter.medication_item_ids)
        self.env["medical.encounter.medication"].create(
            {
                "medical_id": encounter.id,
                "product_id": self.product_03.id,
                "location_id": self.location.id,
            }
        ).run()
        self.assertEqual(1, len(encounter.medication_item_ids))
        self.assertTrue(encounter.medication_item_ids)
        self.env["medical.encounter.medication"].create(
            {
                "medical_id": encounter.id,
                "product_id": self.product_03.id,
                "location_id": self.location.id,
            }
        ).run()
        self.assertTrue(medication_requests)
        self.assertFalse(medication_requests.mapped("medication_administration_ids"))
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertTrue(encounter.sale_order_ids)
        self.assertGreater(self.session.encounter_count, 0)
        self.assertGreater(self.session.sale_order_count, 0)
        self.assertEqual(self.session.action_view_encounters()["res_id"], encounter.id)
        medication_requests.refresh()
        self.assertTrue(medication_requests.mapped("medication_administration_ids"))
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "payment_method_id": self.session.payment_method_ids.ids[0],
            }
        ).run()
        self.assertTrue(
            self.env["stock.picking"].search([("encounter_id", "=", encounter.id)])
        )

    def test_onchange_medication(self):
        self.action.is_billable = False
        encounter, careplan, group = self.create_careplan_and_group(self.agreement_line)
        with Form(
            self.env["medical.medication.item"].with_context(
                default_encounter_id=encounter.id,
            )
        ) as item:
            item.product_id = self.product_03
            self.assertEqual(10, item.price)
            item.qty = 10
            self.assertEqual(100, item.amount)
            item.location_id = self.location

    def test_bom(self):
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        self.env["mrp.bom"].create(
            {
                "product_id": self.product_03.id,
                "product_tmpl_id": self.product_03.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [(0, 0, {"product_id": self.product_extra.id})],
            }
        )
        self.env["medical.encounter.medication"].create(
            {
                "medical_id": encounter.id,
                "product_id": self.product_03.id,
                "location_id": self.location.id,
            }
        ).run()
        self.assertEqual(2, len(encounter.medication_item_ids))
        self.assertEqual(
            1,
            len(encounter.medication_item_ids.filtered(lambda r: r.is_phantom)),
        )
