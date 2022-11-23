# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import json

from odoo import tools
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestCbMedicalDiagnosticReport(TransactionCase):
    def setUp(self):
        super(TestCbMedicalDiagnosticReport, self).setUp()
        self.user_1 = self.env["res.users"].create(
            {
                "name": "Test user",
                "login": "test_report_user",
                "groups_id": [
                    (
                        4,
                        self.env.ref(
                            "medical_diagnostic_report."
                            "group_medical_diagnostic_report_manager"
                        ).id,
                    )
                ],
            }
        )
        self.department_1 = self.env["medical.department"].create(
            {
                "name": "Department 1",
                "with_department_report_header": True,
                "diagnostic_report_header": "Report Header 1",
                "user_ids": [(4, self.user_1.id)],
            }
        )
        self.department_2 = self.env["medical.department"].create(
            {
                "name": "Department 2",
                "with_department_report_header": True,
                "diagnostic_report_header": "Report Header 2",
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
        self.template_1 = self.env["medical.diagnostic.report.template"].create(
            {
                "name": "Template 1",
                "with_observation": False,
                "with_conclusion": True,
                "conclusion": "Everything is ok",
                "with_composition": False,
                "report_category_id": self.category_1.id,
            }
        )
        self.template_2 = self.env["medical.diagnostic.report.template"].create(
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
        self.report = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.signature_1 = self.env["res.users.signature"].create(
            {
                "user_id": self.env.user.id,
                "signature": base64.b64encode(b"12345"),
            }
        )
        self.env.user.current_signature_id = self.signature_1.id

    def test_security(self):
        user_2 = self.env["res.users"].create(
            {
                "name": "Test user",
                "login": "test_report_user_2",
                "groups_id": [
                    (
                        4,
                        self.env.ref(
                            "medical_diagnostic_report."
                            "group_medical_diagnostic_report_manager"
                        ).id,
                    ),
                ],
            }
        )
        department_2 = self.env["medical.department"].create(
            {
                "name": "Department 2",
                "diagnostic_report_header": "Report Header 2",
                "user_ids": [(4, user_2.id)],
            }
        )
        category_3 = self.env["medical.report.category"].create(
            {"name": "Category 3", "medical_department_id": department_2.id}
        )
        report_1 = self._generate_report(self.template_1)
        self.assertTrue(report_1.with_user(self.user_1).is_editable)
        self.assertFalse(report_1.with_user(user_2.id).is_editable)
        self.assertTrue(report_1.with_user(self.user_1.id).is_cancellable)
        self.assertFalse(report_1.with_user(user_2.id).is_cancellable)
        template_2 = self.env["medical.diagnostic.report.template"].create(
            {"name": "Template", "report_category_id": self.category_2.id}
        )
        report_2 = self._generate_report(template_2)
        self.assertTrue(report_2.with_user(self.user_1.id).is_editable)
        self.assertTrue(report_2.with_user(user_2.id).is_editable)
        self.assertTrue(report_2.with_user(self.user_1.id).is_cancellable)
        self.assertTrue(report_2.with_user(user_2.id).is_cancellable)
        template_3 = self.env["medical.diagnostic.report.template"].create(
            {"name": "Template", "report_category_id": category_3.id}
        )
        report_3 = self._generate_report(template_3)
        self.assertFalse(report_3.with_user(self.user_1.id).is_editable)
        self.assertTrue(report_3.with_user(user_2.id).is_editable)
        self.assertFalse(report_3.with_user(self.user_1.id).is_cancellable)
        self.assertTrue(report_3.with_user(user_2.id).is_cancellable)

    def _generate_report(self, template):
        report_generation = self.env[
            "medical.encounter.create.diagnostic.report"
        ].create({"encounter_id": self.encounter_1.id, "template_id": template.id})
        action = report_generation.generate()
        return self.env[action.get("res_model")].browse(action.get("res_id"))

    def test_report_generation(self):
        self.assertEqual("medical.diagnostic.report", self.report._name)
        self.assertEqual(
            self.template_1.report_category_id.id,
            self.report.report_category_id.id,
        )
        self.assertTrue(self.template_1.medical_department_id.id)
        self.assertTrue(self.report.with_department)
        self.assertRegex(
            self.report.medical_department_header,
            self.template_1.medical_department_header,
        )

    def test_finalization(self):
        self.assertNotEqual(self.report.state, "final")
        self.report.registered2final_action()
        self.assertTrue(self.report.with_department)
        self.assertRegex(
            self.report.medical_department_header,
            self.template_1.medical_department_header,
        )
        self.assertTrue(self.report.signature_id.id)
        self.assertEqual(
            self.report.signature_id.id, self.env.user.current_signature_id.id
        )
        self.assertEqual(
            self.report.issued_user_id.digital_signature,
            self.env.user.digital_signature,
        )

    def test_copy_action(self):
        self.report.registered2final_action()
        self.assertEqual(self.report.state, "final")
        action = self.report.copy_action()
        report_duplicate = self.env[action.get("res_model")].browse(
            action.get("res_id")
        )
        self.assertEqual("medical.diagnostic.report", report_duplicate._name)
        self.assertNotEqual(report_duplicate.id, self.report.id)
        self.assertEqual(report_duplicate.state, "registered")
        self.assertEqual(report_duplicate.encounter_id, self.report.encounter_id)

    def test_images(self):
        image = tools.file_open(
            name="addons/cb_medical_diagnostic_report/static/description/icon.png",
            mode="rb",
        ).read()
        self.assertFalse(self.report.image_ids)
        self.report.add_image_attachment(name="icon.png", datas=image)
        self.assertTrue(self.report.image_ids)
        self.report.registered2final_action()
        self.assertEqual(self.report.state, "final")
        serializer = json.loads(self.report.serializer_current)
        self.assertIn("images", serializer)
        self.assertEqual(1, len(serializer["images"]))
