from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMedicationAPI(TransactionCase):
    def setUp(self):
        super().setUp()

        # CINFADOL IBUPROFENO 50 mg/g GEL
        self.wizard = self.env["wizard.create.medication"].create(
            {"register_number": "65747"}
        )
        self.wizard.create_medication()

    def test_create_medication(self):
        product = self.env["product.product"].search(
            [("register_number", "=", "65747")], limit=1
        )
        self.assertEqual(
            product.medication_name, "CINFADOL IBUPROFENO 50 mg/g GEL",
        )
        self.assertTrue(product)
        self.assertTrue(product.is_medication)
        self.assertTrue(product.leaflet)
        self.assertTrue(product.data_sheet)
        self.assertFalse(product.over_the_counter)

        product_template = product.product_tmpl_id
        self.assertTrue(product_template)
        self.assertEqual(product_template.name, "Ibuprofeno")

        # IBUDOL 50 MG/G GEL
        self.wizard.write({"register_number": "62054"})
        self.wizard.create_medication()
        product_template.refresh()

        self.assertEqual(len(product_template.product_variant_ids), 2)

    def test_create_medication_fail(self):
        with self.assertRaises(ValidationError):
            self.wizard.create_medication()

        # Unregistered number
        self.wizard.write({"register_number": "123456789"})
        with self.assertRaises(ValidationError):
            self.wizard.create_medication()

    def test_check_medication_changes(self):
        product = self.env["product.product"].search(
            [("register_number", "=", "65747")], limit=1
        )
        product.write({"psum": True})
        results = [
            {
                "nregistro": "65747",
                "fecha": 1582098933000,
                "tipoCambio": 3,
                "cambio": ["ft", "prosp", "psum"],
            }
        ]
        product_messages = len(product.message_ids)
        self.env["product.product"].process_medication_changes(results)

        self.assertFalse(product.psum)
        self.assertEqual(len(product.message_ids), product_messages + 1)

        self.env["product.product"]._cron_check_medication_changes(
            [65747], "01/12/1990"
        )
