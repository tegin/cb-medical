from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSequence(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.center = self.env["res.partner"].create(
            {
                "name": "Center",
                "is_medical": True,
                "is_center": True,
                "encounter_sequence_prefix": "S",
            }
        )
        self.encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id, "center_id": self.center.id}
        )
        self.product = self.env["product.product"].create(
            {"name": "Product", "type": "consu"}
        )
        self.uom_unit = self.env.ref("uom.product_uom_unit")

    def check_model(self, model, vals):
        values = vals.copy()
        values.update(patient_id=self.patient.id)
        request_1 = self.env[model].create(values)
        self.assertNotEqual(
            request_1.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        values = vals.copy()
        values.update(patient_id=self.patient.id, encounter_id=self.encounter.id)
        request_2 = self.env[model].create(values)
        self.assertEqual(
            request_2.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        values = vals.copy()
        values.update(patient_id=self.patient.id)
        request_3 = (
            self.env[model]
            .with_context(default_encounter_id=self.encounter.id)
            .create(values)
        )
        self.assertEqual(
            request_3.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        return request_1, request_2, request_3

    def test_careplan(self):
        self.check_model("medical.careplan", {})

    def test_procedure(self):
        self.check_model("medical.procedure", {})

    def test_procedure_request(self):
        request_1, request_2, request_3 = self.check_model(
            "medical.procedure.request", {}
        )
        event_1 = request_1.generate_event()
        self.assertFalse(event_1.encounter_id)
        self.assertNotEqual(
            event_1.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        event_2 = request_2.generate_event()
        self.assertTrue(event_2.encounter_id)
        self.assertEqual(
            event_2.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        event_3 = request_3.generate_event()
        self.assertTrue(event_3.encounter_id)
        self.assertEqual(
            event_3.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )

    def test_request_group(self):
        self.check_model("medical.request.group", {})

    def test_laboratory_event(self):
        request = self.env["medical.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        self.check_model(
            "medical.laboratory.event",
            {
                "patient_id": self.patient.id,
                "laboratory_request_id": request.id,
            },
        )

    def test_laboratory_request(self):
        request = self.env["medical.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        self.check_model(
            "medical.laboratory.request",
            {
                "patient_id": self.patient.id,
                "laboratory_request_id": request.id,
            },
        )

    def test_medication_administration(self):
        self.check_model(
            "medical.medication.administration",
            {
                "product_id": self.product.id,
                "product_uom_id": self.uom_unit.id,
            },
        )

    def test_medication_request(self):
        request_1, request_2, request_3 = self.check_model(
            "medical.medication.request",
            {
                "product_id": self.product.id,
                "product_uom_id": self.uom_unit.id,
            },
        )
        event_1 = request_1.generate_event()
        self.assertFalse(event_1.encounter_id)
        self.assertNotEqual(
            event_1.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        event_2 = request_2.generate_event()
        self.assertTrue(event_2.encounter_id)
        self.assertEqual(
            event_2.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        event_3 = request_3.generate_event()
        self.assertTrue(event_3.encounter_id)
        self.assertEqual(
            event_3.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )

    def test_document_reference(self):
        document_type = self.env["medical.document.type"].create(
            {
                "name": "CI",
                "report_action_id": self.browse_ref(
                    "medical_document.action_report_document_report_base"
                ).id,
            }
        )
        self.env["medical.document.type.lang"].create(
            {
                "lang": "en_US",
                "document_type_id": document_type.id,
                "text": "<p>I, ${object.patient_id.name}, recognize the protocol"
                " ${object.name} and sign this document.</p>"
                "<p>Signed:${object.patient_id.name}<br></p>",
            }
        )
        document_type.post()
        self.check_model(
            "medical.document.reference",
            {"document_type_id": document_type.id},
        )

    def test_diagnostic_report(self):
        self.check_model("medical.diagnostic.report", {})

    def test_encounter(self):
        with self.assertRaises(ValidationError):
            self.env["medical.encounter"].create(
                {"patient_id": self.patient.id, "center_id": False}
            )

    def test_res_partner(self):
        vals = {"name": "Prova"}
        exemple = self.env["res.partner"].create(vals)
        exemple.write(
            {"encounter_sequence_prefix": self.center.encounter_sequence_prefix}
        )
        exemple.write({"encounter_sequence_prefix": "O", "encounter_sequence_id": 15})
