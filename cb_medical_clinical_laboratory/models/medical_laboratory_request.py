# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalLaboratoryRequest(models.Model):
    _inherit = "medical.laboratory.request"

    laboratory_service_ids = fields.Many2many(
        "product.product",
        readonly=True,
        domain=[("laboratory_request_ok", "=", True)],
    )
    event_coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement",
        compute="_compute_event_coverage_agreement_id",
    )
    only_allowed_laboratory_services = fields.Boolean()

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

    def _generate_sample_vals(self):
        result = super()._generate_sample_vals()
        result["laboratory_service_ids"] = [
            (6, 0, self.laboratory_service_ids.ids)
        ]
        return result

    def _check_accept_event(self, event):
        result = super()._check_accept_event(event)
        if not result:
            return result
        if not self.only_allowed_laboratory_services:
            return True
        return event.service_id in self._get_laboratory_services()

    def _get_laboratory_services(self):
        return (
            self.laboratory_service_ids
            | self.laboratory_service_ids.mapped(
                "laboratory_service_ids.product_variant_ids"
            )
        )


class MedicalLaboratorySample(models.Model):
    _inherit = "medical.laboratory.sample"

    laboratory_service_ids = fields.Many2many("product.product", readonly=True)
    laboratory_event_ids = fields.One2many(
        string="Laboratory Events",
        states={
            "draft": [("readonly", False)],
            "active": [("readonly", False)],
        },
    )
