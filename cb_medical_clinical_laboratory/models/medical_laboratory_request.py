# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalLaboratoryRequest(models.Model):
    _inherit = "medical.laboratory.request"

    laboratory_service_ids = fields.Many2many(
        "medical.laboratory.service", readonly=True
    )
    event_coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement",
        compute="_compute_event_coverage_agreement_id",
    )

    @api.depends("service_id", "coverage_id.coverage_template_id", "center_id")
    def _compute_event_coverage_agreement_id(self):
        for record in self:
            cai = self.env["medical.coverage.agreement.item"].get_item(
                record.service_id,
                record.coverage_id.coverage_template_id,
                record.center_id,
            )
            agreement = self.env["medical.coverage.agreement"]
            if cai:
                agreement = cai.coverage_agreement_id
            record.event_coverage_agreement_id = agreement


class MedicalLaboratorySample(models.Model):
    _inherit = "medical.laboratory.sample"

    laboratory_service_ids = fields.Many2many(
        "medical.laboratory.service", readonly=True
    )
    laboratory_event_ids = fields.One2many(
        string="Laboratory Events",
        states={
            "draft": [("readonly", False)],
            "active": [("readonly", False)],
        },
    )
    event_coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement",
        compute="_compute_event_coverage_agreement_id",
    )

    @api.depends("service_id", "coverage_id.coverage_template_id", "center_id")
    def _compute_event_coverage_agreement_id(self):
        for record in self:
            cai = self.env["medical.coverage.agreement.item"].get_item(
                record.service_id,
                record.coverage_id.coverage_template_id,
                record.center_id,
            )
            agreement = self.env["medical.coverage.agreement"]
            if cai:
                agreement = cai.coverage_agreement_id
            record.event_coverage_agreement_id = agreement

    def _generate_sample_domain(self):
        return [("encounter_id", "=", self.encounter_id.id)]

    @api.model_create_multi
    def create(self, vals_list):
        records = super(MedicalLaboratoryRequest, self).create(vals_list)
        for record in records:
            record._generate_sample()
        return records

    def _generate_sample(self):
        sample = self.env["medical.laboratory.sample"].search(
            self._generate_sample_domain(), limit=1
        )
        if not sample:
            sample = self.env["medical.laboratory.sample"].create(
                self._generate_sample_vals()
            )
        return sample

    def _generate_sample_vals(self):
        return {
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id,
            "center_id": self.center_id.id,
        }
