# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TestMedicalCoverageAgreement(TransactionCase):

    def setUp(self):
        super(TestMedicalCoverageAgreement, self).setUp()
        self.medical_user_group = \
            self.env.ref('medical_base.group_medical_configurator')
        self.medical_user = self._create_user('medical_user',
                                              self.medical_user_group.id)
        self.patient_model = self.env['medical.patient']
        self.coverage_model = self.env['medical.coverage']
        self.coverage_template_model = self.env['medical.coverage.template']
        self.payor_model = self.env['res.partner']
        self.coverage_agreement_model = self.env['medical.coverage.agreement']
        self.coverage_agreement_model_item = \
            self.env['medical.coverage.agreement.item']
        self.location_model = self.env['res.partner']
        self.product_model = self.env['product.product']
        self.type_model = self.env['workflow.type']
        self.act_def_model = self.env['workflow.activity.definition']
        self.action_model = self.env['workflow.plan.definition.action']
        self.plan_model = self.env['workflow.plan.definition']
        self.patient_1 = self._create_patient()
        self.patient_2 = self._create_patient()
        self.payor_1 = self._create_payor()
        self.coverage_template_1 = self._create_coverage_template()
        self.coverage = self._create_coverage(self.coverage_template_1)
        self.location_1 = self._create_location()
        self.product_1 = self._create_product('test 1')
        self.product_2 = self._create_product('test 2')
        self.type_1 = self._create_type()
        self.act_def_1 = self._create_act_def()
        self.action_1 = self._create_action()
        self.plan_1 = self._create_plan()

    def _create_user(self, name, group_ids):
        return self.env['res.users'].with_context(
            {'no_reset_password': True}).create(
            {'name': name,
             'password': 'demo',
             'login': name,
             'email': '@'.join([name, '@test.com']),
             'groups_id': [(6, 0, [group_ids])]
             })

    def _create_patient(self):
        return self.patient_model.create({
            'name': 'Test patient',
            'gender': 'female',
        })

    def _create_payor(self):
        return self.payor_model.create({
            'name': 'Test payor',
            'is_payor': True,
        })

    def _create_coverage_template(self, state=False):
        vals = {
            'name': 'test coverage template',
            'payor_id': self.payor_1.id,
        }
        if state:
            vals.update({'state': state, })
        coverage_template = self.coverage_template_model.create(vals)
        return coverage_template

    def _create_coverage(self, coverage_template, state=False, patient=False):
        vals = {
            'name': 'test coverage',
            'patient_id': self.patient_1.id,
            'coverage_template_id': coverage_template.id,
        }
        if state:
            vals.update({'state': state, })
        if patient:
            vals.update({'patient_id': patient.id, })
        coverage = self.coverage_model.create(vals)
        return coverage

    def _create_coverage_agreement_item(self, coverage_agreement, product):
        return self.coverage_agreement_model_item.create({
            'coverage_agreement_id': coverage_agreement.id,
            'plan_definition_id': self.plan_1.id,
            'product_id': product.id,
            'total_price': 100,
            'coverage_percentage': 100,
        })

    def _create_location(self):
        return self.location_model.create({
            'name': 'Test location',
            'is_location': True
        })

    def _create_product(self, name):
        return self.product_model.create({
            'name': name,
        })

    def _create_type(self):
        return self.type_model.create({
            'name': 'Test type',
            'model_id': self.browse_ref(
                'medical_administration.model_medical_patient').id,
            'model_ids': [(4, self.browse_ref(
                'medical_administration.model_medical_patient').id)],
        })

    def _create_act_def(self):
        return self.act_def_model.create({
            'name': 'Test activity',
            'model_id': self.type_1.model_id.id,
            'service_id': self.product_1.id,
        })

    def _create_action(self):
        return self.action_model.create({
            'name': 'Test action',
            'activity_definition_id': self.act_def_1.id,
            'type_id': self.type_1.id,
        })

    def _create_plan(self):
        return self.plan_model.create({
            'name': 'Test plan',
            'direct_action_ids': self.action_1,
            'type_id': self.type_1.id,
        })

    def _create_coverage_agreement(self, coverage_template):
        return self.coverage_agreement_model.create({
            'name': 'test coverage agreement',
            'location_ids': [(6, 0, [self.location_1.id])],
            'company_id': self.ref('base.main_company'),
            'coverage_template_ids': [(6, 0, [coverage_template.id])],
            'principal_concept': 'coverage',
        })

    def test_security(self):
        coverage_template = self._create_coverage_template()
        coverage_agreement_vals = {
            'name': 'test coverage agreement',
            'location_ids': [(6, 0, [self.location_1.id])],
            'company_id': self.ref('base.main_company'),
            'coverage_template_ids': [(6, 0, [coverage_template.id])],
        }
        coverage_agreement = self.coverage_agreement_model.\
            sudo(self.medical_user).create(coverage_agreement_vals)
        self.assertNotEquals(coverage_agreement, False)
        item_1 = self._create_coverage_agreement_item(
            coverage_agreement, self.product_1)
        coverage_agreement.action_search_item()
        self.assertEquals(item_1.coverage_price, 100)
        self.assertEquals(item_1.private_price, 0)

    def test_add_agreement_items(self):
        coverage_template = self._create_coverage_template()
        coverage_agreement = self._create_coverage_agreement(coverage_template)
        vals = {
            'coverage_agreement_id': coverage_agreement.id,
            'plan_definition_id': self.plan_1.id,
            'product_id': self.product_1.id,
            'total_price': 100,
        }
        self.coverage_agreement_model_item.create(vals)
        self.assertEquals(len(coverage_agreement.item_ids), 1)

    def test_change_prices(self):
        # case 1
        coverage_agreement_vals = {
            'name': 'test coverage agreement',
            'location_ids': [(6, 0, [self.location_1.id])],
            'company_id': self.ref('base.main_company'),
        }
        coverage_agreement = self.coverage_agreement_model.create(
            coverage_agreement_vals)
        self.assertNotEquals(coverage_agreement, False)
        item_1 = self.coverage_agreement_model_item.create({
            'coverage_agreement_id': coverage_agreement.id,
            'plan_definition_id': self.plan_1.id,
            'product_id': self.product_1.id,
            'coverage_percentage': 50.0,
            'total_price': 200})
        self.assertEquals(item_1.coverage_price, 100)
        self.assertEquals(item_1.private_price, 100)
        wiz = self.env['medical.agreement.change.prices'].create({
            'difference': 50.0})
        wiz.with_context(active_ids=[item_1.id]).change_prices()
        self.assertEquals(item_1.coverage_price, 150)
        self.assertEquals(item_1.private_price, 150)

    def test_onchange_period(self):
        # case 1
        coverage_agreement_vals = {
            'name': 'test coverage agreement',
            'location_ids': [(6, 0, [self.location_1.id])],
            'company_id': self.ref('base.main_company'),
            'date_from': (datetime.today() + relativedelta(days=5))
        }
        coverage_agreement = self.coverage_agreement_model.create(
            coverage_agreement_vals)
        coverage_agreement._onchange_date_range()
        self.assertEquals(coverage_agreement.active, False)
        # case 2
        coverage_agreement.date_from = datetime.today() - \
            relativedelta(days=10)
        coverage_agreement._onchange_date_range()
        self.assertEquals(coverage_agreement.active, True)
        # case 3
        coverage_agreement.date_to = datetime.today() + relativedelta(
            days=100)
        coverage_agreement._onchange_date_range()
        self.assertEquals(coverage_agreement.active, True)
        # case 4
        coverage_agreement.date_to = datetime.today() - relativedelta(
            days=5)
        coverage_agreement._onchange_date_range()
        self.assertEquals(coverage_agreement.active, False)
