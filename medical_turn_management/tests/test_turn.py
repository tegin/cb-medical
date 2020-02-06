# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields


class TestTurn(TransactionCase):

    def setUp(self):
        super().setUp()
        self.specialty_01 = self.env['medical.turn.specialty'].create({
            'name': 'Specialty 01',
            'rule_ids': [(0, 0, {
                'dayofweek': '0',
                'start_hour': 8,
                'duration': 1,
            })]
        })
        self.specialty_02 = self.env['medical.turn.specialty'].create({
            'name': 'Specialty 02',
            'rule_ids': [(0, 0, {
                'dayofweek': '1',
                'start_hour': 8,
                'duration': 1,
            })]
        })

    def test_generation_filtered(self):
        self.assertFalse(self.env['medical.turn'].search([
            ('specialty_id', 'in', [
                self.specialty_01.id, self.specialty_02.id])
        ]))
        self.env['wzd.medical.turn'].create({
            'turn_specialty_ids': [(4, self.specialty_01.id)],
            'start_date': '2020-01-01',
            'end_date': '2020-01-31',
        }).doit()
        turns = self.env['medical.turn'].search([
            ('specialty_id', 'in', [self.specialty_01.id])
        ])
        self.assertTrue(turns)
        for turn in turns:
            self.assertEqual(fields.Datetime.from_string(
                turn.date
            ).weekday(), 0)
        self.assertFalse(self.env['medical.turn'].search([
            ('specialty_id', 'in', [self.specialty_01.id]),
            '|', ('date', '>=', '2020-02-01'),
            ('date', '<', '2020-01-01')
        ]))
        self.assertFalse(self.env['medical.turn'].search([
            ('specialty_id', 'in', [self.specialty_02.id])
        ]))

    def test_generation_all(self):
        self.assertFalse(self.env['medical.turn'].search([
            ('specialty_id', 'in', [
                self.specialty_01.id, self.specialty_02.id])
        ]))
        self.env['wzd.medical.turn'].create({
            'start_date': '2020-01-01',
            'end_date': '2020-01-31',
        }).doit()
        turns = self.env['medical.turn'].search([
            ('specialty_id', 'in', [self.specialty_01.id])
        ])
        self.assertTrue(turns)
        for turn in turns:
            self.assertEqual(fields.Datetime.from_string(
                turn.date
            ).weekday(), 0)
        self.assertFalse(self.env['medical.turn'].search([
            ('specialty_id', 'in', [self.specialty_01.id]),
            '|', ('date', '>=', '2020-02-01'),
            ('date', '<', '2020-01-01')
        ]))
        turns = self.env['medical.turn'].search([
            ('specialty_id', 'in', [self.specialty_02.id])
        ])
        self.assertTrue(turns)
        for turn in turns:
            self.assertEqual(fields.Datetime.from_string(
                turn.date
            ).weekday(), 1)

        self.assertFalse(self.env['medical.turn'].search([
            ('specialty_id', 'in', [self.specialty_02.id]),
            '|', ('date', '>=', '2020-02-01'),
            ('date', '<', '2020-01-01')
        ]))
