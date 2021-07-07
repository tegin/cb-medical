# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    def get_coverage(self, template, coverage, **kwargs):
        self.ensure_one()
        magnetic_str = kwargs["magnetic_str"]
        subscriber_id = kwargs["subscriber_id"]
        if coverage.state == "draft":
            coverage.subscriber_id = subscriber_id
        if coverage.subscriber_id != subscriber_id:
            coverage = False
        if coverage and coverage.coverage_template_id != template:
            coverage = False
        if not coverage:
            coverage = self.coverage_ids.filtered(
                lambda r: (
                    r.coverage_template_id == template
                    and r.state in ["active", "draft"]
                    and r.subscriber_id == subscriber_id
                )
            )
        if not coverage:
            coverage = self.env["medical.coverage"].create(
                {
                    "patient_id": self.id,
                    "coverage_template_id": template.id,
                    "subscriber_id": subscriber_id,
                }
            )
        if coverage.state == "draft":
            coverage.draft2active()
        self.coverage_ids.filtered(
            lambda r: (
                r.id != coverage.id
                and r.coverage_template_id == template
                and r.state == "active"
            )
        ).active2cancelled()
        if magnetic_str and coverage.subscriber_magnetic_str != magnetic_str:
            coverage.write({"subscriber_magnetic_str": magnetic_str})
        return coverage
