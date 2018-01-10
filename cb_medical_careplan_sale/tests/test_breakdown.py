# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from .test_careplan_sale import TestMedicalCareplanSale
from odoo.exceptions import ValidationError


class TestMedicalCareplanSaleBreakdown(TestMedicalCareplanSale):

    def setUp(self):
        super(TestMedicalCareplanSaleBreakdown, self).setUp()
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True

    def create_careplan_and_group(self):
        careplan = self.env['medical.careplan'].create({
            'patient_id': self.patient.id,
            'coverage_id': self.coverage.id,
        })
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': self.agreement_line.id,
        })
        self.action.is_billable = False
        wizard.run()
        group = self.env['medical.request.group'].search([
            ('careplan_id', '=', careplan.id)])
        group.ensure_one()
        return careplan, group

    def test_no_agreement(self):
        careplan, group = self.create_careplan_and_group()
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        with self.assertRaises(ValidationError):
            group.breakdown()

    def test_no_breakdown(self):
        self.plan_definition.is_breakdown = False
        careplan, group = self.create_careplan_and_group()
        self.assertTrue(group.is_billable)
        self.assertFalse(group.is_breakdown)
        with self.assertRaises(ValidationError):
            group.breakdown()

    def test_correct(self):
        careplan, group = self.create_careplan_and_group()
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_aux.id,
            'coverage_agreement_id': self.agreement.id,
            'total_price': 110,
            'coverage_percentage': 0.5
        })
        group.breakdown()
        self.assertFalse(group.is_billable)
        self.assertFalse(group.is_breakdown)
        careplan.create_sale_order()
        self.assertGreater(len(careplan.sale_order_ids), 0)
        return careplan
