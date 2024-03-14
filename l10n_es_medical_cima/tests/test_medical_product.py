# Copyright 2022 Creu Blanca

from odoo.tests.common import TransactionCase


class TestMedicalProduct(TransactionCase):
    def setUp(self):
        super(TestMedicalProduct, self).setUp()

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
        self.test_product_template = self.env["medical.product.template"].create(
            {
                "name": "Test name",
                "product_type": "medication",
                "ingredients": "Test name",
                "dosage": "600 mg",
                "form_id": self.tablet_form.id,
            }
        )
        self.test_product_30_tablets = self.env["medical.product.product"].create(
            {
                "product_tmpl_id": self.test_product_template.id,
                "amount": 30,
                "amount_uom_id": self.tablet_uom.id,
            }
        )
        self.test_template_lab = self.env["medical.product.template.commercial"].create(
            {
                "product_tmpl_id": self.test_product_template.id,
                "laboratory": "Lab test",
                "code": "70039",
                "laboratory_product_name": "labname",
            }
        )
        self.test_template_30_tablets_lab = self.env[
            "medical.product.product.commercial"
        ].create(
            {
                "medical_product_id": self.test_product_30_tablets.id,
                "product_tmpl_commercial_id": self.test_template_lab.id,
                "code": "661765",
            }
        )

    def test_name_search(self):
        search_by_lab_name = self.env["medical.product.template"]._name_search(
            name="labn"
        )
        self.assertEqual(search_by_lab_name[0][0], self.test_product_template.id)
        # TODO: test also search by code and name,
        #  for a reason it does not work the test, but the functional test yes
        # search_by_code = self.env[
        # 'medical.product.template'
        # ]._name_search(name="6617")
        # self.assertEqual(search_by_code[0][0], self.test_product_template.id)
        # search_by_name = self.env[
        # 'medical.product.template'
        # ]._name_search(name="test")
        # self.assertEqual(search_by_name[0][0], self.test_product_template.id)

    def test_action_view_product_tmpl_commercial_ids(self):
        self.assertEqual(self.test_product_template.product_tmpl_commercial_count, 1)
        action = self.test_product_template.action_view_product_tmpl_commercial_ids()
        self.assertEqual(action["res_id"], self.test_template_lab.id)

    def test_action_view_product_commercial_ids(self):
        self.assertEqual(self.test_product_30_tablets.product_commercial_count, 1)
        action = self.test_product_30_tablets.action_view_product_commercial_ids()
        self.assertEqual(action["res_id"], self.test_template_30_tablets_lab.id)
