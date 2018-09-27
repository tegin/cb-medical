from odoo.tests.common import TransactionCase


class TestClinicalLaboratory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env['medical.patient'].create({
            'name': 'Patient'
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
