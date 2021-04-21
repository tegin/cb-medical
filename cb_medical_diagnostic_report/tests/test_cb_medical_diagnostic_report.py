# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.tests import TransactionCase


class TestCbMedicalDiagnosticReport(TransactionCase):
    def setUp(self):
        super(TestCbMedicalDiagnosticReport, self).setUp()
        self.department_1 = self.env["medical.department"].create(
            {
                "name": "Department 1",
                "diagnostic_report_header": " Report Header 1",
            }
        )
        self.category_1 = self.env["medical.report.category"].create(
            {
                "name": "Category 1",
                "medical_department_id": self.department_1.id,
            }
        )
        self.category_2 = self.env["medical.report.category"].create(
            {"name": "Category 2"}
        )
        self.patient_1 = self.env["medical.patient"].create(
            {"name": "Patient 1", "vat": "47238567H"}
        )
        self.center_1 = self.env["res.partner"].create(
            {
                "name": "Center 1",
                "is_center": True,
                "encounter_sequence_prefix": "C",
            }
        )
        self.encounter_1 = self.env["medical.encounter"].create(
            {
                "name": "Encounter 1",
                "patient_id": self.patient_1.id,
                "center_id": self.center_1.id,
            }
        )
        self.template_1 = self.env[
            "medical.diagnostic.report.template"
        ].create(
            {
                "name": "Template 1",
                "with_observation": False,
                "with_conclusion": True,
                "conclusion": "Everything is ok",
                "with_composition": False,
                "report_category_id": self.category_1.id,
            }
        )
        self.template_2 = self.env[
            "medical.diagnostic.report.template"
        ].create(
            {
                "name": "Template 2",
                "with_observation": False,
                "with_conclusion": True,
                "conclusion": "Everything is ok",
                "with_composition": False,
                "report_category_id": self.category_2.id,
            }
        )

        report_generation = self.env[
            "medical.encounter.create.diagnostic.report"
        ].create(
            {
                "encounter_id": self.encounter_1.id,
                "template_id": self.template_1.id,
            }
        )
        action = report_generation.generate()
        self.report = self.env[action.get("res_model")].browse(
            action.get("res_id")
        )
        self.signature_1 = self.env["res.users.signature"].create(
            {
                "user_id": self.env.user.id,
                "signature": base64.b64encode(b"12345"),
            }
        )
        self.env.user.current_signature_id = self.signature_1.id

    def test_report_generation(self):
        self.assertEqual("medical.diagnostic.report", self.report._name)
        self.assertEqual(
            self.template_1.report_category_id.id,
            self.report.report_category_id.id,
        )
        self.assertTrue(self.template_1.medical_department_id.id)
        self.assertTrue(self.report.with_department)
        self.assertRegex(
            self.template_1.medical_department_header,
            self.report.medical_department_header,
        )

    def test_finalization(self):
        self.assertNotEqual(self.report.state, "final")
        self.report.registered2final_action()
        self.assertTrue(self.report.with_department)
        self.assertRegex(
            self.template_1.medical_department_header,
            self.report.medical_department_header,
        )
        self.assertTrue(self.report.signature_id.id)
        self.assertEqual(
            self.report.signature_id.id, self.env.user.current_signature_id.id
        )
        self.assertEqual(
            self.report.issued_user_id.digital_signature,
            self.env.user.digital_signature,
        )

    def test_report_expand(self):
        report_generation = self.env[
            "medical.encounter.create.diagnostic.report"
        ].create(
            {
                "encounter_id": self.encounter_1.id,
                "template_id": self.template_2.id,
            }
        )
        action = report_generation.generate()
        report = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertFalse(report.with_department)
        self.assertTrue(self.template_1.medical_department_id)
        self.env["medical.diagnostic.report.expand"].create(
            {
                "diagnostic_report_id": report.id,
                "template_id": self.template_1.id,
            }
        ).merge()
        self.assertTrue(report.with_department)
        self.assertRegex(
            report.medical_department_header,
            self.template_1.medical_department_header,
        )
