# Copyright 2022 Creu Blanca

from odoo.tests.common import TransactionCase


class TestMedicalProductCommercial(TransactionCase):
    def setUp(self):
        super(TestMedicalProductCommercial, self).setUp()

        self.tablet_uom = self.env["uom.uom"].create(
            {
                "name": "Tablets",
                "category_id": self.env.ref("uom.product_uom_categ_unit").id,
                "factor": 1.0,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )
        self.tablet_form = self.env["medication.form"].create(
            {
                "name": "EFG film coated tablets",
                "uom_ids": [(4, self.tablet_uom.id)],
            }
        )
        self.ibuprofen_template = self.env["medical.product.template"].create(
            {
                "name": "Ibuprofen",
                "product_type": "medication",
                "ingredients": "Ibuprofen",
                "dosage": "600 mg",
                "form_id": self.tablet_form.id,
            }
        )
        self.ibuprofen_30_tablets = self.env["medical.product.product"].create(
            {
                "product_tmpl_id": self.ibuprofen_template.id,
                "amount": 30,
                "amount_uom_id": self.tablet_uom.id,
            }
        )
        self.ibuprofen_template_cinfa = self.env[
            "medical.product.template.commercial"
        ].create(
            {
                "product_tmpl_id": self.ibuprofen_template.id,
                "laboratory": "Cinfa",
                "code": "70039",
                "laboratory_product_name": "laboratory_name",
            }
        )
        self.ibuprofen_30_tablets_cinfa = self.env[
            "medical.product.product.commercial"
        ].create(
            {
                "medical_product_id": self.ibuprofen_30_tablets.id,
                "product_tmpl_commercial_id": self.ibuprofen_template_cinfa.id,
                "code": "661426",
            }
        )

    def test_name_commercial_template(self):
        self.assertRegex(
            self.ibuprofen_template_cinfa.name,
            "Ibuprofen 600 mg EFG film coated tablets  Cinfa",
        )

    def test_name_commercial_product(self):
        self.assertRegex(
            self.ibuprofen_30_tablets_cinfa.name,
            "661426 Ibuprofen 600 mg EFG film coated tablets 30.0 Tablets  Cinfa",
        )

    def test_action_view_medical_product_commercial_ids(self):
        self.assertEqual(self.ibuprofen_template_cinfa.product_count, 1)
        action = (
            self.ibuprofen_template_cinfa.action_view_medical_product_commercial_ids()
        )
        self.assertEqual(action["res_id"], self.ibuprofen_30_tablets_cinfa.id)

    def test_compute_product_tmpl_commercial_domain(self):
        self.assertRegex(
            self.ibuprofen_30_tablets_cinfa.product_tmpl_commercial_domain,
            "%s" % self.ibuprofen_template.id,
        )
        product_commercial_2 = self.env["medical.product.product.commercial"].create(
            {"code": "1111"}
        )
        self.assertRegex(product_commercial_2.product_tmpl_commercial_domain, "%s" % 0)
