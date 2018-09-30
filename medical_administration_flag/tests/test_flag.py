# Copyright 2017 LasLabs Inc.
# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestMedicalAdministrationFlag(TransactionCase):

    def test_service(self):
        category = self.env['medical.flag.category'].create({
            'name': 'Category'
        })
        patient = self.env['medical.patient'].create({
            'name': 'Patient'
        })
        self.assertEqual(patient.medical_flag_count, 0)
        flag = self.env['medical.flag'].create({
            'patient_id': patient.id,
            'description': 'Description',
            'category_id': category.id
        })
        self.assertEqual(patient.medical_flag_count, 1)
        action = patient.action_view_flags()
        self.assertEqual(action['res_id'], flag.id)
        self.assertTrue(flag.active)
        self.assertFalse(flag.closure_date)
        flag.close()
        self.assertFalse(flag.active)
        self.assertTrue(flag.closure_date)
