from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMedication(TransactionCase):
    def setUp(self):
        super().setUp()
        self.category = self.env["product.category"].create({"name": "Category"})
        self.service = self.env["product.product"].create(
            {"name": "Service", "type": "service"}
        )
        self.partner = self.env["res.partner"].create({"name": "supplier"})
        self.product = self.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
                "categ_id": self.category.id,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "name": self.partner.id,
                "product_name": "SUPPROD",
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_id": self.product.id,
            }
        )

    def test_search(self):
        self.assertFalse(self.env["product.product"]._name_search("SUPPROD"))
        search = (
            self.env["product.product"]
            .with_context(search_on_supplier=True)
            .name_search("SUPPROD")
        )
        self.assertTrue(search)
        self.assertEqual(self.product.id, search[0][0])

    def test_constrains_service(self):
        with self.assertRaises(ValidationError):
            self.env["product.category"].create(
                {"name": "Categ", "category_product_id": self.product.id}
            )
