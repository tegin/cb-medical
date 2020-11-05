from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductActivity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.template = self.env["product.template"].create(
            {"type": "service", "name": "Product"}
        )
        self.product = self.template.product_variant_id

    def test_raise_error_product_01(self):
        self.template.type = "consu"
        with self.assertRaises(ValidationError):
            self.product._generate_activity()

    def test_raise_error_product_02(self):
        self.product._generate_activity()
        with self.assertRaises(ValidationError):
            self.template.type = "consu"

    def test_activity(self):
        activity = self.product._generate_activity()
        self.product.refresh()
        self.assertTrue(activity)
        self.assertEqual(self.product, activity.service_id)
        self.assertEqual(self.product.activity_definition_ids, activity)
        self.assertEqual(activity, self.product._generate_activity())
        self.assertEqual(activity.id, self.product.get_activity()["res_id"])

    def test_activity_views(self):
        action = self.product.generate_activity()
        activity = self.env["workflow.activity.definition"].browse(
            action["res_id"]
        )
        self.assertTrue(activity)
        self.assertEqual(activity, self.product._generate_activity())
        self.assertEqual(activity.id, self.product.get_activity()["res_id"])

    def test_multi_product_raise(self):
        self.product._generate_activity()
        product = self.env["product.product"].create(
            {"product_tmpl_id": self.template.id}
        )
        with self.assertRaises(ValidationError):
            product.generate_activity()

    def test_multi_activity_raise(self):
        self.product._generate_activity()
        with self.assertRaises(ValidationError):
            self.env["workflow.activity.definition"].create(
                self.product._get_activity_vals()
            )
