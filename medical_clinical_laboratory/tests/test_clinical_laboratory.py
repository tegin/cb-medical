from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestClinicalLaboratory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env['medical.patient'].create({
            'name': 'Patient'
        })
        self.patient2 = self.env['medical.patient'].create({
            'name': 'Test Patient2'
        })

    def test_constrains(self):
        request = self.env['medical.laboratory.request'].create({
            'patient_id': self.patient.id
        })
        with self.assertRaises(ValidationError):
            self.env['medical.laboratory.request'].create({
                'patient_id': self.patient2.id,
                'laboratory_request_id': request.id,
            })

    def test_constrains_event(self):
        request = self.env['medical.laboratory.request'].create({
            'patient_id': self.patient.id
        })
        with self.assertRaises(ValidationError):
            self.env['medical.laboratory.event'].create({
                'patient_id': self.patient2.id,
                'laboratory_request_id': request.id,
            })

    def test_laboratory(self):
        request = self.env['medical.laboratory.request'].create({
            'patient_id': self.patient.id,
        })
        self.assertEqual(request.laboratory_event_count, 0)
        event = request.generate_event()
        self.assertEqual(request.laboratory_event_count, 1)
        self.assertEqual(
            event.id,
            request.action_view_laboratory_events()['res_id']
        )
