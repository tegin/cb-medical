# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo import fields
import dateutil.relativedelta


class TesitMedicalCommission(TransactionCase):

    def setUp(self):
        super(TesitMedicalCommission, self).setUp()
        self.patient_model = self.env['medical.patient']
        self.product_model = self.env['product.product']
        self.type_model = self.env['workflow.type']
        self.act_def_model = self.env['workflow.activity.definition']
        self.action_model = self.env['workflow.plan.definition.action']
        self.plan_model = self.env['workflow.plan.definition']
        self.role_model = self.env['medical.role']
        self.practitioner_model = self.env['res.partner']
        self.procedure_request_model = self.env['medical.procedure.request']
        self.procedure_model = self.env['medical.procedure']
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line_model = self.env['sale.order.line']
        self.account_invoice_model = self.env['account.invoice']
        self.settle_model = self.env['sale.commission.settlement']
        self.make_settle_model = self.env['sale.commission.make.settle']
        self.commission_model = self.env['sale.commission']
        self.patient_1 = self._create_patient()
        self.product_1 = self._create_product('test 1')
        self.product_2 = self._create_product('test 2')
        self.type_1 = self.browse_ref('medical_workflow.medical_workflow')
        self.act_def_1 = self._create_act_def()
        self.plan_1 = self._create_plan()
        self.action_1 = self._create_action()
        self.role_1 = self._create_role()
        self.practitioner_1 = self._create_practitioner('pr1')
        self.practitioner_2 = self._create_practitioner('pr2')
        self.customer = self._create_customer('Test Customer')
        self.commission_section_paid = self.commission_model.create({
            'name': 'Section commission - Payment Based',
            'commission_type': 'section',
            'invoice_state': 'open',
            'sections': [
                (0, 0, {
                    'amount_from': 1.0,
                    'amount_to': 100.0,
                    'percent': 10.0,
                })]
            })

    def _create_patient(self):
        return self.patient_model.create({
            'name': 'Test patient',
            'gender': 'female',
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
            'direct_plan_definition_id': self.plan_1.id,
            'type_id': self.type_1.id,
        })

    def _create_plan(self):
        return self.plan_model.create({
            'name': 'Test plan',
            'type_id': self.type_1.id,
        })

    def _create_role(self):
        return self.role_model.create({
            'name': 'Nurse',
            'description': 'Nurse'
        })

    def _create_practitioner(self, name):
        return self.practitioner_model.create({
            'name': name,
            'practitioner_role_ids': [(6, 0, self.role_1.ids)],
            'is_practitioner': True,
        })

    def _create_customer(self, name):
        return self.env['res.partner'].create({
            'name': name,
            'email': 'example@yourcompany.com',
            'customer': True,
            'phone': 123456,
            'currency_id': self.env.ref('base.EUR'),
        })

    def _create_sale_order(self):
        self.practitioner_1.agent = True
        so = self.sale_order_model.create({
            'partner_id': self.customer.id,
        })
        agent = self.browse_ref(
            'sale_commission.res_partner_pritesh_sale_agent')
        commission = self.commission_section_paid
        sol1 = self.sale_order_line_model.create({
            'product_id': self.product_2.id,
            'product_uom_qty': 1,
            'order_id': so.id,
            'agents': [(0, 0, {'agent': agent.id,
                               'commission': commission.id})]
        })
        sol2 = self.sale_order_line_model.create({
            'product_id': self.product_2.id,
            'product_uom_qty': 2,
            'order_id': so.id
        })

        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 1
        sol2.qty_delivered = 2
        return so

    def _create_invoice_from_sale(self, sale):
        data = {'advance_payment_method': 'delivered'}
        payment = self.env['sale.advance.payment.inv'].create(data)
        sale_context = {
            'active_id': sale.id,
            'active_ids': sale.ids,
            'active_model': 'sale.order',
            'open_invoices': True,
        }
        res = payment.with_context(sale_context).create_invoices()
        invoice_id = self.env['account.invoice'].browse(res['res_id'])
        return invoice_id

    def test_medical_commission(self):
        # add fees in medical services
        self.assertTrue(self.action_1.make_invisible)
        self.product_1.medical_commission = True
        self.action_1.variable_fee = 30.0
        self.action_1.fixed_fee = 60.0

        # add commission agent to practitioner
        agent = self.browse_ref(
            'sale_commission.res_partner_pritesh_sale_agent')
        self.practitioner_1.agents = [(6, 0, agent.ids)]

        # create procedure request and procedure
        pr = self.procedure_request_model.create({
            'patient_id': self.patient_1.id,
        })
        self.assertTrue(pr.make_invisible)
        pr.service_id = self.product_1
        self.assertFalse(pr.make_invisible)
        pr.performer_id = self.practitioner_1
        pr.fixed_fee = 100
        pr.variable_fee = 80
        p = pr.generate_event()
        self.assertFalse(p.make_invisible)
        self.assertEquals(p.fixed_fee, 100)
        self.assertEquals(p.variable_fee, 80)
        p.performer_id = self.practitioner_2.id
        p._onchange_performer_id()
        self.assertEquals(p.commission_agent_id,
                          self.practitioner_2)

    def test_make_settlements(self):
        so = self._create_sale_order()
        self._create_invoice_from_sale(so).action_invoice_open()

        # make settlement
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        settlements = self.settle_model.search([('state', '=', 'settled')])
        self.assertEqual(len(settlements), 1)
