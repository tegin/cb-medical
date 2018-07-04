# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


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
        self.template2 = self.env['medical.coverage.template'].create({
            'name': 'Template2',
            'payor_id': self.payor.id
        })
        self.center = self.env['res.partner'].create({
            'name': 'Location',
            'encounter_sequence_prefix': 'S',
            'is_center': True,
        })
        self.coverage = self.env['medical.coverage'].create({
            'patient_id': self.patient.id,
            'coverage_template_id': self.template.id,
        })
        self.coverage2 = self.env['medical.coverage'].create({
            'patient_id': self.patient.id,
            'coverage_template_id': self.template2.id,
        })
        self.encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient.id,
            'center_id': self.center.id,
        })
        self.careplan = self.env['medical.careplan'].create({
            'patient_id': self.patient.id,
            'coverage_id': self.coverage.id,
            'encounter_id': self.encounter.id,
            'center_id': self.encounter.center_id.id,
        })
        self.format = self.env['medical.authorization.format'].create({
            'code': 'Format',
            'name': 'Format test',
            'authorization_format': '^[0-9]{2}$'
        })
        self.agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Agreement',
            'center_ids': [(6, 0, self.center.ids)],
            'coverage_template_ids': [
                (4, self.template.id), (4, self.template2.id)],
            'company_id': self.browse_ref('base.main_company').id,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.only_number').id,
            'authorization_format_id': self.format.id,
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
        ].with_context(
            default_coverage_agreement_id=self.agreement.id
        ).create({
            'coverage_agreement_id': self.agreement.id,
            'product_id': self.product.id,
            'plan_definition_id': self.plan_definition.id,
            'total_price': 100,
            'coverage_percentage': 0,
        })

    def test_wizard_failure(self):
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': self.careplan.id,
            'agreement_line_id': self.agreement_line.id,
            'authorization_number': '222'
        })
        self.assertEqual(wizard.patient_id, self.patient)
        self.assertTrue(wizard.plan_definition_id)
        with self.assertRaises(ValidationError):
            wizard.run()

    def test_wizard(self):
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': self.careplan.id,
            'agreement_line_id': self.agreement_line.id,
            'authorization_number': '22'
        })
        self.assertFalse(self.patient.last_coverage_id)
        self.assertEqual(wizard.patient_id, self.patient)
        self.assertTrue(wizard.plan_definition_id)
        wizard.run()
        careplans = self.env['medical.careplan'].search([
            ('careplan_id', '=', self.careplan.id),
        ])
        self.assertGreater(len(careplans.ids), 0)
        self.assertEqual(self.patient.last_coverage_id, self.coverage)
        careplan = self.env['medical.careplan'].create({
            'patient_id': self.patient.id,
            'coverage_id': self.coverage2.id,
            'encounter_id': self.encounter.id,
            'center_id': self.encounter.center_id.id,
        })

        self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': self.agreement_line.id,
            'authorization_number': '22'
        }).run()

        self.assertEqual(self.patient.last_coverage_id, self.coverage2)
