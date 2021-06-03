# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCoverage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.payor = self.env["res.partner"].create(
            {"name": "Payor", "is_payor": True}
        )
        self.template = self.env["medical.coverage.template"].create(
            {"name": "Template", "payor_id": self.payor.id}
        )

    def test_simple(self):
        coverage = self.env["medical.coverage"].create(
            {
                "patient_id": self.patient.id,
                "coverage_template_id": self.template.id,
            }
        )
        self.assertFalse(coverage.subscriber_required)

    def test_failure(self):
        self.template.subscriber_required = True
        self.template.subscriber_format = "^[0-9]{12}$"
        coverage = self.env["medical.coverage"].new(
            {
                "patient_id": self.patient.id,
                "coverage_template_id": self.template.id,
                "subscriber_id": "12345",
            }
        )
        with self.assertRaises(ValidationError):
            coverage.create(coverage._convert_to_write(coverage._cache))
        coverage = self.env["medical.coverage"].new(
            {
                "patient_id": self.patient.id,
                "coverage_template_id": self.template.id,
                "subscriber_id": "123456789012",
            }
        )
        coverage = coverage.create(coverage._convert_to_write(coverage._cache))
        self.assertEqual(coverage.subscriber_id, "123456789012")
