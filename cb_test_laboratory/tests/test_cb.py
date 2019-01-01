# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.cb_test.tests.test_cb import TestCB
from odoo.exceptions import ValidationError


class TestCBSale(TestCB):

    def test_laboratory(self):
        self.plan_definition.is_billable = True
        self.plan_definition.is_breakdown = False
        self.action4 = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.lab_activity.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': False,
            'name': 'Action4',
        })
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(group.laboratory_request_ids)
        action = group.with_context(
            model_name='medical.laboratory.request'
        ).action_view_request()
        self.assertEqual(
            group.laboratory_request_ids,
            self.env['medical.laboratory.request'].search(action['domain']))
        with self.assertRaises(ValidationError):
            self.env['wizard.medical.encounter.close'].create({
                'encounter_id': encounter.id,
                'pos_session_id': self.session.id,
            }).run()
        for lab_req in group.laboratory_request_ids:
            self.assertEqual(lab_req.laboratory_event_count, 0)
            event = lab_req.generate_event({
                'is_sellable_insurance': True,
                'is_sellable_private': True,
                'private_amount': 20,
                'performer_id': self.practitioner_01.id,
                'coverage_amount': 10,
                'private_cost': 18,
                'coverage_cost': 9,
                'laboratory_code': '1234',
            })
            self.assertEqual(
                event.id, lab_req.action_view_laboratory_events()['res_id'])
            self.assertEqual(lab_req.laboratory_event_count, 1)
            lab_req.generate_event({
                'is_sellable_insurance': False,
                'is_sellable_private': False,
                'private_amount': 20,
                'laboratory_code': '12345',
                'performer_id': self.practitioner_01.id,
                'coverage_amount': 10,
                'private_cost': 18,
                'coverage_cost': 9,
            })
            self.assertEqual(lab_req.laboratory_event_count, 2)
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertIn(encounter.state, ['finished', 'onleave'])
        self.assertTrue(
            encounter.sale_order_ids.mapped('order_line').filtered(
                lambda r: r.laboratory_event_id
            )
        )
        self.assertGreater(
            sum(a.amount for a in encounter.sale_order_ids.mapped(
                'order_line').filtered(
                    lambda r: r.laboratory_event_id
                ).mapped('agents')), 0)
