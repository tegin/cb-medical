# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMedicalCareplanSale(TransactionCase):

    def setUp(self):
        super(TestMedicalCareplanSale, self).setUp()
        self.payor = self.env['res.partner'].create({
            'name': 'Payor',
            'is_payor': True,
        })
        self.coverage_template = self.env['medical.coverage.template'].create({
            'payor_id': self.payor.id,
            'name': 'Coverage',
        })
        self.patient = self.env['medical.patient'].create({
            'name': 'Patient'
        })
        self.coverage = self.env['medical.coverage'].create({
            'patient_id': self.patient.id,
            'coverage_template_id': self.coverage_template.id,
        })
        self.agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Agreement',
            'coverage_template_ids': [(4, self.coverage_template.id)],
            'company_id': self.browse_ref('base.main_company').id,
        })
        self.product = self.env['product.product'].create({
            'type': 'service',
            'name': 'MR',
        })
        self.product_aux = self.env['product.product'].create({
            'type': 'service',
            'name': 'INF',
        })
        self.type = self.browse_ref('medical_workflow.medical_workflow')
        self.plan_definition = self.env['workflow.plan.definition'].create({
            'name': 'Plan',
            'type_id': self.type.id,
            'is_billable': True,
        })
        self.activity = self.env['workflow.activity.definition'].create({
            'name': 'Activity',
            'service_id': self.product_aux.id,
            'model_id': self.browse_ref('medical_clinical_procedure.'
                                        'model_medical_procedure_request').id,
            'type_id': self.type.id,
        })
        self.action = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': True,
            'name': 'Action'
        })
        self.agreement_line = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product.id,
            'coverage_agreement_id': self.agreement.id,
            'plan_definition_id': self.plan_definition.id,
            'total_price': 100,
            'coverage_percentage': 0.5
        })

    def test_careplan_sale(self):
        careplan = self.env['medical.careplan'].create({
            'patient_id': self.patient.id,
            'coverage_id': self.coverage.id,
        })
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': self.agreement_line.id,
        })
        with self.assertRaises(ValidationError):
            wizard.run()
        self.action.is_billable = False
        wizard.run()
        groups = self.env['medical.request.group'].search([
            ('careplan_id', '=', careplan.id)])
        self.assertTrue(groups)
        careplan.create_sale_order()
        self.assertGreater(len(careplan.sale_order_ids), 0)
        procedure_requests = self.env['medical.procedure.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(procedure_requests), 0)
        return careplan
