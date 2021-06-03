# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestCoverage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.payor = self.env["res.partner"].create(
            {"is_medical": "True", "name": "Payor", "is_payor": True}
        )
        self.template = self.env["medical.coverage.template"].create(
            {"payor_id": self.payor.id, "name": "Coverage"}
        )
        self.template_2 = self.env["medical.coverage.template"].create(
            {"payor_id": self.payor.id, "name": "Coverage 2"}
        )

    def test_activate_coverage(self):
        coverage = self.env["medical.coverage"].create(
            {
                "patient_id": self.patient.id,
                "coverage_template_id": self.template.id,
                "subscriber_id": "2",
            }
        )
        coverage_2 = self.patient.get_coverage(
            self.template, coverage, subscriber_id="1", magnetic_str="magnetic"
        )
        self.assertEqual(coverage, coverage_2)
        self.assertEqual(coverage_2.subscriber_id, "1")

    def test_coverage(self):
        coverage = self.patient.get_coverage(
            self.template,
            self.env["medical.coverage"],
            subscriber_id="1",
            magnetic_str="magnetic",
        )
        self.assertEqual(coverage.state, "active")
        self.assertTrue(coverage)
        coverage_2 = self.patient.get_coverage(
            self.template,
            self.env["medical.coverage"],
            subscriber_id="1",
            magnetic_str="magnetic2",
        )
        self.assertEqual(coverage, coverage_2)
        self.assertEqual(coverage.state, "active")
        self.assertEqual(coverage_2.subscriber_magnetic_str, "magnetic2")
        coverage_3 = self.patient.get_coverage(
            self.template_2,
            coverage,
            subscriber_id="1",
            magnetic_str="magnetic",
        )
        self.assertNotEqual(coverage, coverage_3)
        coverage_4 = self.patient.get_coverage(
            self.template, coverage, subscriber_id="2", magnetic_str="magnetic"
        )
        self.assertNotEqual(coverage, coverage_4)
