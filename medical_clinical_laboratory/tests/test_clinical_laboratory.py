from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestClinicalLaboratory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.patient2 = self.env["medical.patient"].create(
            {"name": "Test Patient2"}
        )

    def test_constrains(self):
        request = self.env["medical.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        with self.assertRaises(ValidationError):
            self.env["medical.laboratory.request"].create(
                {
                    "patient_id": self.patient2.id,
                    "laboratory_request_id": request.id,
                }
            )

    def test_constrains_event(self):
        request = self.env["medical.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        with self.assertRaises(ValidationError):
            self.env["medical.laboratory.event"].create(
                {
                    "patient_id": self.patient2.id,
                    "laboratory_request_id": request.id,
                }
            )

    def test_laboratory_sample(self):
        request = self.env["medical.laboratory.sample"].create(
            {"patient_id": self.patient.id}
        )
        self.assertEqual(request.laboratory_event_count, 0)
        self.assertEqual(request.laboratory_request_count, 0)
        event = request.generate_event()
        self.assertEqual(request.laboratory_event_count, 1)
        self.assertEqual(
            event.id, request.action_view_laboratory_events()["res_id"]
        )
        request.action_view_request_parameters()
        event2 = request.generate_event()
        action = request.action_view_laboratory_events()
        events = self.env[action["res_model"]].search(action["domain"])
        self.assertEqual(events, event | event2)

    def test_laboratory_sample_consistency(self):
        request = self.env["medical.laboratory.sample"].create(
            {"patient_id": self.patient.id}
        )
        request.generate_event()
        with self.assertRaises(ValidationError):
            request.patient_id = self.patient2

    def test_laboratory_request(self):
        request = self.env["medical.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        # Samples are no childs of the request
        self.assertFalse(request.laboratory_sample_ids)
        self.assertEqual(request.laboratory_sample_count, 0)
        self.assertEqual(request.laboratory_event_count, 0)
        self.assertEqual(request.laboratory_request_count, 0)
        event = self.env["medical.laboratory.event"].create(
            {
                "laboratory_request_id": request.id,
                "patient_id": self.patient.id,
            }
        )
        self.assertEqual(request.laboratory_event_count, 1)
        self.assertEqual(
            event.id, request.action_view_laboratory_events()["res_id"]
        )
        request.action_view_request_parameters()
        event2 = self.env["medical.laboratory.event"].create(
            {
                "laboratory_request_id": request.id,
                "patient_id": self.patient.id,
            }
        )
        action = request.action_view_laboratory_events()
        events = self.env[action["res_model"]].search(action["domain"])
        self.assertEqual(events, event | event2)

    def test_laboratory_request_consistency(self):
        request = self.env["medical.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        self.env["medical.laboratory.event"].create(
            {
                "laboratory_request_id": request.id,
                "patient_id": self.patient.id,
            }
        )
        with self.assertRaises(ValidationError):
            request.patient_id = self.patient2
