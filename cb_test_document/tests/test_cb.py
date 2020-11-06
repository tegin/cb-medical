# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import base64

from mock import patch
from odoo.addons.cb_test.tests.test_cb import TestCB
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import at_install, post_install


@post_install(True)
@at_install(False)
class TestCBDocument(TestCB):
    @patch(
        "odoo.addons.base_report_to_printer.models.printing_printer."
        "PrintingPrinter.print_file"
    )
    def test_document(self, mock):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.patient_01.lang = self.lang_en.code
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertEqual(
            encounter.id,
            self.env["medical.encounter"].find_encounter_by_barcode(
                encounter.internal_identifier
            )["res_id"],
        )
        identifier = encounter.internal_identifier
        self.assertFalse(
            self.env["medical.encounter"]
            .find_encounter_by_barcode(
                "{}-{}-{}".format(identifier, identifier, identifier)
            )
            .get("res_id", False)
        )
        self.assertTrue(careplan.document_reference_ids)
        self.assertTrue(group.document_reference_ids)
        documents = group.document_reference_ids.filtered(
            lambda r: r.document_type == "action"
        )
        self.assertTrue(documents)
        for document in documents:
            self.assertEqual(
                encounter.id,
                self.env["medical.encounter"].find_encounter_by_barcode(
                    document.internal_identifier
                )["res_id"],
            )
            with self.assertRaises(ValidationError):
                # Raises: State must be Current
                document.current2superseded()
            self.assertEqual(document.state, "draft")
            self.assertTrue(document.is_editable)
            self.assertFalse(document.text)
            # Print the document. Status of the document changes to 'current'
            document.view()
            with self.assertRaises(ValidationError):
                # Raises: State must be draft
                document.draft2current()
            self.assertEqual(document.state, "current")
            # Once the document has been printed is not editable anymore.
            self.assertFalse(document.is_editable)
            self.assertTrue(document.text)
            self.assertEqual(
                document.text,
                "<p>%s</p><p>%s</p>"
                % (self.patient_01.lang, self.patient_01.name),
            )
            self.patient_01.name = self.patient_01.name + " Other name"
            document.view()
            self.assertEqual(document.state, "current")
            self.assertEqual(document.lang, self.patient_01.lang)
            # Subsequent changes to the patient or other master data
            # Are not reflected in the document.
            self.assertNotEqual(
                document.text,
                "<p>%s</p><p>%s</p>"
                % (self.patient_01.lang, self.patient_01.name),
            )
            language_change = self.env[
                "medical.document.reference.change.language"
            ].new({"document_reference_id": document.id})
            self.assertEqual(language_change.lang_ids, self.lang_es)
            self.env["medical.document.reference.change.language"].new(
                {
                    "document_reference_id": document.id,
                    "lang_id": self.lang_es.id,
                }
            ).run()
            self.assertEqual(document.lang, self.lang_es.code)
            self.assertEqual(
                document.text,
                "<p>%s</p><p>%s</p>"
                % (self.lang_es.code, self.patient_01.name),
            )
            document.current2superseded()
            self.assertEqual(document.state, "superseded")
            self.assertIsInstance(document.render(), bytes)
            with self.assertRaises(ValidationError):
                document.current2superseded()
            with patch(
                "odoo.addons.base_remote.models.base.Base.remote",
                new=self.remote,
            ):
                document.print()
                # We must verify that the document print cannot be changed
        documents = group.document_reference_ids.filtered(
            lambda r: r.document_type == "zpl2"
        )
        self.assertTrue(documents)
        for document in documents:
            self.assertEqual(
                document.render(),
                base64.b64encode(
                    (
                        # Label start
                        "^XA\n"
                        # Print width
                        "^PW480\n"
                        # UTF-8 encoding
                        "^CI28\n"
                        # Label position
                        "^LH10,10\n"
                        # Pased encounter
                        "^FO10,10^A0N,10,10^FD%s^FS\n"
                        # Recall last saved parameters
                        "^JUR\n"
                        # Label end
                        "^XZ"
                        % encounter.internal_identifier
                    ).encode("utf-8")
                ),
            )
            with self.assertRaises(UserError):
                document.view()
            with patch(
                "odoo.addons.base_remote.models.base.Base.remote",
                new=self.remote,
            ):
                document.print()
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.product_02.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 110,
                "coverage_percentage": 0.5,
                "authorization_method_id": self.browse_ref(
                    "cb_medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "cb_medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        group.breakdown()
        self.assertFalse(group.is_billable)
        self.assertFalse(group.is_breakdown)
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertGreater(len(encounter.sale_order_ids), 0)
