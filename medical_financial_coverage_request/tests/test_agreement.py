from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAgreementTemplate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.browse_ref('base.main_company')
        self.product_01 = self.env['product.product'].create({
            'name': 'Product 01'
        })
        self.product_02 = self.env['product.product'].create({
            'name': 'Product 02'
        })
        self.products = self.product_01
        self.products |= self.product_02
        self.template = self.env['medical.coverage.agreement'].create({
            'name': 'Template',
            'company_id': self.company.id,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without'
            ).id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything'
            ).id,
            'is_template': True,
        })
        self.env['medical.coverage.agreement.item'].with_context(
            default_coverage_agreement_id=self.template.id,
        ).create({
            'product_id': self.product_01.id,
            'total_price': 10,
        })
        self.item = self.env['medical.coverage.agreement.item'].with_context(
            default_coverage_agreement_id=self.template.id,
        ).create({
            'product_id': self.product_02.id,
            'total_price': 10,
        })

    def test_constrain_01(self):
        with self.assertRaises(ValidationError):
            self.env['medical.coverage.agreement'].create({
                'name': 'Template',
                'company_id': self.company.id,
                'authorization_method_id': self.browse_ref(
                    'cb_medical_financial_coverage_request.without'
                ).id,
                'authorization_format_id': self.browse_ref(
                    'cb_medical_financial_coverage_request.format_anything'
                ).id,
                'template_id': self.template.id,
                'is_template': True,
            })

    def test_constrain_02(self):
        payor = self.env['res.partner'].create({
            'is_medical': True,
            'is_payor': True,
            'name': 'Payor'
        })
        coverage = self.env['medical.coverage.template'].create({
            'payor_id': payor.id
        })
        with self.assertRaises(ValidationError):
            self.template.write({
                'coverage_template_ids': [(4, coverage.id)]
            })

    def test_copy_agreement_without_items(self):
        agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Template',
            'company_id': self.company.id,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without'
            ).id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything'
            ).id,
        })
        self.env['medical.coverage.agreement.template'].create({
            'agreement_id': agreement.id,
            'template_id': self.template.id
        }).run()
        self.assertEqual(agreement.template_id, self.template)
        self.assertFalse(agreement.item_ids)

    def test_copy_agreement_items(self):
        agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Template',
            'company_id': self.company.id,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without'
            ).id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything'
            ).id,
        })
        self.env['medical.coverage.agreement.template'].create({
            'agreement_id': agreement.id,
            'template_id': self.template.id,
            'set_items': True,
        }).run()
        self.assertEqual(agreement.template_id, self.template)
        self.assertTrue(agreement.item_ids)
        for product in self.products:
            self.assertEqual(
                self.template.item_ids.filtered(
                    lambda r: r.product_id == product).total_price,
                agreement.item_ids.filtered(
                    lambda r: r.product_id == product).total_price
            )

    def test_copy_agreement_items_partially(self):
        agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Template',
            'company_id': self.company.id,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without'
            ).id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything'
            ).id,
        })
        self.env['medical.coverage.agreement.item'].with_context(
            default_coverage_agreement_id=agreement.id,
        ).create({
            'product_id': self.product_02.id,
            'total_price': 20,
        })
        self.env['medical.coverage.agreement.template'].create({
            'agreement_id': agreement.id,
            'template_id': self.template.id,
            'set_items': True,
        }).run()
        self.assertEqual(agreement.template_id, self.template)
        self.assertTrue(agreement.item_ids)
        self.assertEqual(
            self.template.item_ids.filtered(
                lambda r: r.product_id == self.product_01).total_price,
            agreement.item_ids.filtered(
                lambda r: r.product_id == self.product_01).total_price
        )
        self.assertNotEqual(
            self.template.item_ids.filtered(
                lambda r: r.product_id == self.product_02).total_price,
            agreement.item_ids.filtered(
                lambda r: r.product_id == self.product_02).total_price
        )

    def test_constrains(self):
        with self.assertRaises(ValidationError):
            self.env['medical.coverage.agreement.item'].with_context(
                default_coverage_agreement_id=self.template.id,
            ).create({
                'product_id': self.product_02.id,
                'total_price': 10,
            })

    def test_no_constrains(self):
        self.item.write({'active': False})
        self.env['medical.coverage.agreement.item'].with_context(
            default_coverage_agreement_id=self.template.id,
        ).create({
            'product_id': self.product_02.id,
            'total_price': 10,
        })
