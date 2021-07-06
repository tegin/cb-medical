# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestMedicalDocumentZPL2(TransactionCase):
    def setUp(self):
        super().setUp()
        self.label_zpl2 = self.env["printing.label.zpl2"].create(
            {
                "name": "label1",
                "model_id": self.env.ref(
                    "medical_document.model_medical_document_reference"
                ).id,
                "component_ids": [
                    (0, 0, {"name": "DEMO", "data": "object.patient_id.name"})
                ],
            }
        )
        self.zpl2_document_type = self.env["medical.document.type"].create(
            {
                "name": "CI",
                "document_type": "zpl2",
                "label_zpl2_id": self.label_zpl2.id,
            }
        )
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.reference = self.env["medical.document.reference"].create(
            {
                "document_type": self.zpl2_document_type.document_type,
                "document_type_id": self.zpl2_document_type.id,
                "patient_id": self.patient.id,
            }
        )

    def test_document_zpl2(self):
        self.assertEqual(self.zpl2_document_type.state, "draft")
        self.zpl2_document_type.draft2current()
        self.assertEqual(self.zpl2_document_type.state, "current")
        self.zpl2_document_type.post()
        self.assertFalse(self.zpl2_document_type.current_template_id)

    def test_render_label_error(self):
        self.label_zpl2.model_id = self.env.ref(
            "base_report_to_printer.model_printing_printer"
        )
        reference = self.env["medical.document.reference"].create(
            {
                "document_type": self.zpl2_document_type.document_type,
                "document_type_id": self.zpl2_document_type.id,
                "patient_id": self.patient.id,
            }
        )
        with self.assertRaises(UserError):
            reference.render_text()

    def test_render_text_error(self):
        self.zpl2_document_type.write({"document_type": "action"})
        with self.assertRaises(UserError):
            self.reference.render_text()
        self.assertNotEqual(self.reference._get_printer_usage(), "label")

    def test_render_label(self):
        self.zpl2_document_type2 = self.env["medical.document.type"].create(
            {
                "name": "CI",
                "document_type": "zpl2",
                "label_zpl2_id": self.label_zpl2.id,
            }
        )
        reference = self.env["medical.document.reference"].create(
            {
                "document_type": self.zpl2_document_type2.document_type,
                "document_type_id": self.zpl2_document_type2.id,
                "patient_id": self.patient.id,
            }
        )
        reference.render()
        self.assertEqual(reference._get_printer_usage(), "label")
