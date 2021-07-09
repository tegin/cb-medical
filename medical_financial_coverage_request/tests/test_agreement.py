from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestAgreementTemplate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.product_01 = cls.env["product.product"].create(
            {"name": "Product 01"}
        )
        cls.product_02 = cls.env["product.product"].create(
            {"name": "Product 02"}
        )
        cls.products = cls.product_01 | cls.product_02
        cls.template = cls.env["medical.coverage.agreement"].create(
            {
                "name": "Template",
                "company_id": cls.company.id,
                "authorization_method_id": cls.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": cls.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
                "is_template": True,
            }
        )
        cls.center = cls.env["res.partner"].create(
            {"name": "Center", "is_center": True}
        )
        cls.item_01 = (
            cls.env["medical.coverage.agreement.item"]
            .with_context(default_coverage_agreement_id=cls.template.id)
            .create({"product_id": cls.product_01.id, "total_price": 10})
        )
        cls.item_02 = (
            cls.env["medical.coverage.agreement.item"]
            .with_context(default_coverage_agreement_id=cls.template.id)
            .create({"product_id": cls.product_02.id, "total_price": 10})
        )
        cls.payor = cls.env["res.partner"].create(
            {"is_medical": True, "is_payor": True, "name": "Payor"}
        )
        cls.coverage = cls.env["medical.coverage.template"].create(
            {"payor_id": cls.payor.id}
        )

    def test_constrain_01(self):
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement"].create(
                {
                    "name": "Template",
                    "company_id": self.company.id,
                    "authorization_method_id": self.browse_ref(
                        "medical_financial_coverage_request.without"
                    ).id,
                    "authorization_format_id": self.browse_ref(
                        "medical_financial_coverage_request.format_anything"
                    ).id,
                    "template_id": self.template.id,
                    "is_template": True,
                }
            )

    def test_constrain_02(self):
        with self.assertRaises(ValidationError):
            self.template.write(
                {"coverage_template_ids": [(4, self.coverage.id)]}
            )

    def test_copy_agreement_without_items(self):
        agreement = self.env["medical.coverage.agreement"].create(
            {
                "name": "Template",
                "company_id": self.company.id,
                "authorization_method_id": self.browse_ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.env["medical.coverage.agreement.template"].create(
            {"agreement_id": agreement.id, "template_id": self.template.id}
        ).run()
        self.assertEqual(agreement.template_id, self.template)
        self.assertFalse(agreement.item_ids)

    def test_copy_agreement_items(self):
        agreement = self.env["medical.coverage.agreement"].create(
            {
                "name": "Template",
                "company_id": self.company.id,
                "authorization_method_id": self.browse_ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.env["medical.coverage.agreement.template"].create(
            {
                "agreement_id": agreement.id,
                "template_id": self.template.id,
                "set_items": True,
            }
        ).run()
        self.assertEqual(agreement.template_id, self.template)
        self.assertTrue(agreement.item_ids)
        for product in self.products:
            self.assertEqual(
                self.template.item_ids.filtered(
                    lambda r: r.product_id == product
                ).total_price,
                agreement.item_ids.filtered(
                    lambda r: r.product_id == product
                ).total_price,
            )

    def test_copy_agreement_items_partially(self):
        agreement = self.env["medical.coverage.agreement"].create(
            {
                "name": "Template",
                "company_id": self.company.id,
                "authorization_method_id": self.browse_ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.env["medical.coverage.agreement.item"].with_context(
            default_coverage_agreement_id=agreement.id
        ).create({"product_id": self.product_02.id, "total_price": 20})
        self.env["medical.coverage.agreement.template"].create(
            {
                "agreement_id": agreement.id,
                "template_id": self.template.id,
                "set_items": True,
            }
        ).run()
        self.assertEqual(agreement.template_id, self.template)
        self.assertTrue(agreement.item_ids)
        self.assertEqual(
            self.template.item_ids.filtered(
                lambda r: r.product_id == self.product_01
            ).total_price,
            agreement.item_ids.filtered(
                lambda r: r.product_id == self.product_01
            ).total_price,
        )
        self.assertNotEqual(
            self.template.item_ids.filtered(
                lambda r: r.product_id == self.product_02
            ).total_price,
            agreement.item_ids.filtered(
                lambda r: r.product_id == self.product_02
            ).total_price,
        )

    def test_constrains(self):
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.item"].with_context(
                default_coverage_agreement_id=self.template.id
            ).create({"product_id": self.product_02.id, "total_price": 10})

    def test_no_constrains(self):
        self.item_02.write({"active": False})
        self.env["medical.coverage.agreement.item"].with_context(
            default_coverage_agreement_id=self.template.id
        ).create({"product_id": self.product_02.id, "total_price": 10})

    def test_get_item_01(self):
        self.template.is_template = False
        self.template.coverage_template_ids = self.coverage
        self.template.center_ids = self.center
        item = self.env["medical.coverage.agreement.item"].get_item(
            self.product_01, self.coverage, self.center
        )
        self.assertEqual(item, self.item_01)

    def test_get_item_02(self):
        self.template.is_template = False
        self.template.coverage_template_ids = self.coverage
        self.template.center_ids = self.center
        item = self.env["medical.coverage.agreement.item"].get_item(
            self.product_01.id, self.coverage.id, self.center.id
        )
        self.assertEqual(item, self.item_01)

    def test_get_item_03(self):
        self.template.is_template = False
        self.template.coverage_template_ids = self.coverage
        self.template.center_ids = self.center
        item = self.env["medical.coverage.agreement.item"].get_item(
            self.product_01.id, self.coverage.id, self.center.id, plan=True
        )
        self.assertFalse(item)

    def test_get_item_04(self):
        self.template.is_template = False
        self.template.coverage_template_ids = self.coverage
        self.template.center_ids = self.center
        self.template.date_from = date.today() + timedelta(days=1)
        item = self.env["medical.coverage.agreement.item"].get_item(
            self.product_01.id, self.coverage.id, self.center.id
        )
        self.assertFalse(item)

    def test_get_item_05(self):
        self.template.is_template = False
        self.template.coverage_template_ids = self.coverage
        self.template.center_ids = self.center
        self.template.date_from = date.today()
        item = self.env["medical.coverage.agreement.item"].get_item(
            self.product_01.id,
            self.coverage.id,
            self.center.id,
            date=date.today() + timedelta(days=-1),
        )
        self.assertFalse(item)

    def test_get_item_06(self):
        self.template.is_template = False
        self.template.coverage_template_ids = self.coverage
        self.template.center_ids = self.center
        self.template.date_from = date.today()
        self.template.date_to = date.today() + timedelta(days=1)
        item = self.env["medical.coverage.agreement.item"].get_item(
            self.product_01.id,
            self.coverage.id,
            self.center.id,
            date=date.today() + timedelta(days=2),
        )
        self.assertFalse(item)
