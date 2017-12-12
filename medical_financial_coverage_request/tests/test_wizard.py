# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestWizard(TransactionCase):
    def setUp(self):
        super(TestWizard, self).setUp()
        self.patient = self.env['medical.patient'].create({
            'name': 'Patient',
        })
        self.payor = self.env['res.partner'].create({
            'name': 'Payor',
            'is_payor': True,
        })
        self.template = self.env['medical.coverage.template'].create({
            'name': 'Template',
            'payor_id': self.payor.id
        })
        self.location = self.env['res.partner'].create({
            'name': 'Location',
            'is_location': True,
        })
        self.coverage = self.env['medical.coverage'].create({
            'patient_id': self.patient.id,
            'coverage_template_id': self.template.id,
        })
        self.careplan = self.env['medical.careplan'].create({
            'patient_id': self.patient.id,
            'coverage_id': self.coverage.id,
        })
        self.agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Agreement',
            'location_ids': [(6, 0, self.location.ids)],
            'coverage_template_ids': [(6, 0, self.template.ids)],
            'company_id': self.browse_ref('base.main_company').id,
        })
        self.product = self.env['product.product'].create({
            'name': 'Product',
            'type': 'service',
        })
        self.plan_definition = self.env['workflow.plan.definition'].create({
            'type_id': self.browse_ref('medical_workflow.medical_workflow').id,
            'name': 'Plan'
        })
        self.activity = self.env['workflow.activity.definition'].create({
            'type_id': self.browse_ref('medical_workflow.medical_workflow').id,
            'name': 'Activity',
            'service_id': self.product.id,
            'quantity': 1,
            'model_id': self.browse_ref(
                'medical_clinical_careplan.model_medical_careplan').id,
        })
        self.env['workflow.plan.definition.action'].create({
            'direct_plan_definition_id': self.plan_definition.id,
            'activity_definition_id': self.activity.id,
            'name': 'Action',
        })
        self.agreement_line = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'coverage_agreement_id': self.agreement.id,
            'product_id': self.product.id,
            'plan_definition_id': self.plan_definition.id,
            'total_price': 100,
            'coverage_percentage': 0,
        })

    def test_wizard(self):
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': self.careplan.id,
            'agreement_line_id': self.agreement_line.id,
        })
        self.assertEqual(wizard.patient_id, self.patient)
        self.assertTrue(wizard.plan_definition_id)
        import logging
        logging.info(wizard._get_values())
        logging.info(wizard.run())
        careplans = self.env['medical.careplan'].search([
            ('careplan_id', '=', self.careplan.id),
        ])
        self.assertGreater(len(careplans.ids), 0)
