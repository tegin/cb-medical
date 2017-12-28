# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.cb_medical_careplan_sale.tests import test_careplan_sale


class TestMedicalCommission(test_careplan_sale.TestMedicalCareplanSale):
    def setUp(self):
        super(TestMedicalCommission, self).setUp()
        self.practitioner = self.env['res.partner'].create({
            'name': 'Practitioner',
            'is_practitioner': True,
            'agent': True,
            'commission': self.browse_ref(
                'cb_medical_commission.commission_01').id,
        })
        self.product.medical_commission = True
        self.action.variable_fee = 1

    def test_careplan_sale(self):
        careplan = super(TestMedicalCommission, self).test_careplan_sale()
        for sale_order in careplan.sale_order_ids:
            sale_order.recompute_lines_agents()
            self.assertEqual(sale_order.commission_total, 0)
        procedure_requests = self.env['medical.procedure.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(procedure_requests), 0)
        for request in procedure_requests:
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner
            procedure.commission_agent_id = self.practitioner
        careplan.recompute_commissions()
        for sale_order in careplan.sale_order_ids:
            sale_order.recompute_lines_agents()
            self.assertGreater(sale_order.commission_total, 0)

        return careplan
