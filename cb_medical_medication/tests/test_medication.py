from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMedication(TransactionCase):
    def setUp(self):
        super().setUp()
        self.category = self.env['product.category'].create({
            'name': 'Category',
        })
        self.service = self.env['product.product'].create({
            'name': 'Service',
            'type': 'service',
        })
        self.product = self.env['product.product'].create({
            'name': 'Product',
            'type': 'product',
            'categ_id': self.category.id,
        })

    def test_constrains_service(self):
        with self.assertRaises(ValidationError):
            self.env['product.category'].create({
                'name': 'Categ',
                'category_product_id': self.product.id,
            })
