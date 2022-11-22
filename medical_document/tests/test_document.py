from mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase


class TestDocument(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        name = "testing_remote_server"
        cls.remote = cls.env["res.remote"].search([("name", "=", name)])
        if not cls.remote:
            cls.remote = cls.env["res.remote"].create(
                {"name": name, "ip": "127.0.0.1", "in_network": True}
            )
        cls.server = cls.env["printing.server"].create(
            {"name": "Server", "address": "localhost", "port": 631}
        )
        cls.printer = cls.env["printing.printer"].create(
            {
                "name": "Printer 1",
                "system_name": "P1",
                "server_id": cls.server.id,
            }
        )
        cls.patient = cls.env["medical.patient"].create({"name": "My patient"})
        cls.lang_es = cls.env.ref("base.lang_es")
        if not cls.lang_es.active:
            cls.lang_es.active = True
        cls.lang_it = cls.env.ref("base.lang_it")
        if not cls.lang_it.active:
            cls.lang_it.active = True
        cls.lang_en = cls.env.ref("base.lang_en")
        if not cls.lang_en.active:
            cls.lang_en.active = True
        cls.document_type = cls.env["medical.document.type"].create(
            {
                "name": "CI",
                "report_action_id": cls.env.ref(
                    "medical_document.action_report_document_report_base"
                ).id,
                "lang_ids": [
                    (
                        0,
                        0,
                        {
                            "lang": cls.lang_en.code,
                            "text": "<p>%s</p><p>${object.patient_id.name}"
                            "</p>" % cls.lang_en.code,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "lang": cls.lang_es.code,
                            "text": "<p>%s</p><p>${object.patient_id.name}"
                            "</p>" % cls.lang_es.code,
                        },
                    ),
                ],
            }
        )
        cls.document_type.post()

    @patch(
        "odoo.addons.base_report_to_printer.models.printing_printer."
        "PrintingPrinter.print_file"
    )
    def test_document(self, mck):
        document = self.env["medical.document.reference"].create(
            {
                "patient_id": self.patient.id,
                "document_type_id": self.document_type.id,
            }
        )
        self.assertEqual(document.fhir_state, "draft")
        self.assertFalse(document.text)
        # Print the document. Status of the document changes to 'current'
        document.view()
        self.assertEqual(document.fhir_state, "current")
        # Once the document has been printed is not editable anymore.
        self.assertTrue(document.text)
        self.assertEqual(
            document.text,
            "<p>{}</p><p>{}</p>".format(self.patient.lang, self.patient.name),
        )
        self.patient.name = self.patient.name + " Other name"
        document.view()
        self.assertEqual(document.fhir_state, "current")
        self.assertEqual(document.lang, self.patient.lang)
        # Subsequent changes to the patient or other master data
        # Are not reflected in the document.
        self.assertNotEqual(
            document.text,
            "<p>{}</p><p>{}</p>".format(self.patient.lang, self.patient.name),
        )
        language_change = Form(
            self.env["medical.document.reference.change.language"].with_context(
                default_document_reference_id=document.id
            )
        )
        language_change.lang_id = self.lang_es
        language_change.save().run()
        self.assertEqual(document.lang, self.lang_es.code)
        self.assertEqual(
            document.text,
            "<p>{}</p><p>{}</p>".format(self.lang_es.code, self.patient.name),
        )
        document.current2superseded()
        self.assertEqual(document.fhir_state, "superseded")
        self.assertIsInstance(document.render(), bytes)
        with patch(
            "odoo.addons.base_remote.models.base.Base.remote",
            new=self.remote,
        ):
            document.print()
        mck.assert_not_called()
        self.env["res.remote.printer"].create(
            {
                "remote_id": self.remote.id,
                "printer_id": self.printer.id,
                "is_default": True,
            }
        )
        with patch(
            "odoo.addons.base_remote.models.base.Base.remote",
            new=self.remote,
        ):
            document.print()
        mck.assert_called_once()

    def test_document_constrain_01(self):
        document = self.env["medical.document.reference"].create(
            {
                "patient_id": self.patient.id,
                "document_type_id": self.document_type.id,
            }
        )
        with self.assertRaises(ValidationError):
            # Raises: State must be Current
            document.current2superseded()

    def test_document_constrain_02(self):
        document = self.env["medical.document.reference"].create(
            {
                "patient_id": self.patient.id,
                "document_type_id": self.document_type.id,
            }
        )
        self.assertEqual(document.fhir_state, "draft")
        self.assertFalse(document.text)
        # Print the document. Status of the document changes to 'current'
        document.view()
        with self.assertRaises(ValidationError):
            # Raises: State must be draft
            document.draft2current()

    def test_document_constrain_03(self):
        document = self.env["medical.document.reference"].create(
            {
                "patient_id": self.patient.id,
                "document_type_id": self.document_type.id,
            }
        )
        self.assertEqual(document.fhir_state, "draft")
        self.assertFalse(document.text)
        # Print the document. Status of the document changes to 'current'
        document.view()
        document.current2superseded()
        self.assertEqual(document.fhir_state, "superseded")
        self.assertIsInstance(document.render(), bytes)
        with self.assertRaises(ValidationError):
            document.current2superseded()

    def test_document_constrain_04(self):
        document = self.env["medical.document.reference"].create(
            {
                "patient_id": self.patient.id,
                "document_type_id": self.document_type.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["medical.document.reference"].create(
                {
                    "patient_id": self.patient.id,
                    "document_type_id": self.document_type.id,
                    "document_reference_id": document.id,
                }
            )

    def test_document_no_lang(self):
        self.patient.lang = self.lang_it.code
        document = self.env["medical.document.reference"].create(
            {
                "patient_id": self.patient.id,
                "document_type_id": self.document_type.id,
            }
        )
        document.view()
        self.assertEqual(document.lang, self.lang_it.code)
        self.assertNotEqual(
            document.text,
            "<p>{}</p><p>{}</p>".format(self.patient.lang, self.patient.name),
        )
