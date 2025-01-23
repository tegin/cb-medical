from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMedication(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["product.category"].create({"name": "Category"})
        cls.service = cls.env["product.product"].create(
            {"name": "Service", "type": "service"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "supplier"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
                "categ_id": cls.category.id,
            }
        )
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.partner.id,
                "product_name": "SUPPROD",
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_id": cls.product.id,
            }
        )

    def test_search(self):
        self.assertFalse(self.env["product.product"]._name_search("SUPPROD"))
        search = (
            self.env["product.product"]
            .with_context(search_on_supplier=True)
            ._name_search("SUPPROD")
        )
        self.assertTrue(search)
        self.assertEqual(self.product.id, search[0][0])

    def test_constrains_service(self):
        with self.assertRaises(ValidationError):
            self.env["product.category"].create(
                {"name": "Categ", "category_product_id": self.product.id}
            )
