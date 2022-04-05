# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalLaboratoryEvent(models.Model):
    _inherit = "medical.laboratory.event"

    delay = fields.Date()
    laboratory_code = fields.Char(
        readonly=True,
        store=True,
        compute="_compute_laboratory_code",
    )
    laboratory_service_ids = fields.Many2many(
        related="laboratory_request_id.laboratory_service_ids",
        string="Request Laboratory services",
        domain=[("laboratory_request_ok", "=", True)],
    )
    # TODO: Remove this on the future
    cost = fields.Float(compute="_compute_is_sellable", store=True)
    private_cost = fields.Float(compute="_compute_is_sellable", store=True)
    coverage_cost = fields.Float(compute="_compute_is_sellable", store=True)

    @api.depends("performer_id", "service_id")
    def _compute_laboratory_code(self):
        for record in self:
            seller = record.service_id._select_seller(partner_id=record.performer_id)
            record.laboratory_code = (
                seller.product_code or record.service_id.default_code
            )

    def _compute_sellable_fields(self):
        super(MedicalLaboratoryEvent, self)._compute_sellable_fields()
        seller = self.service_id._select_seller(partner_id=self.performer_id)
        self.cost = seller.price or self.service_id.standard_price
        cai = self.coverage_agreement_item_id
        if not self.is_billable or not cai:
            self.coverage_cost = 0
            self.private_cost = 0
            return
        self.coverage_cost = self.cost * cai.coverage_percentage / 100
        self.private_cost = self.cost - self.coverage_cost

    def _get_is_billable(self):
        if (
            self.laboratory_request_id
            and self.service_id in self.laboratory_request_id.laboratory_service_ids
        ):
            return False
        return super(MedicalLaboratoryEvent, self)._get_is_billable()

    @api.onchange("laboratory_service_id", "laboratory_request_id")
    def _onchange_laboratory_service(self):
        for rec in self:
            rec.laboratory_code = rec.laboratory_service_id.laboratory_code
            rec.name = rec.laboratory_service_id.name
            cov = rec.laboratory_request_id.careplan_id.coverage_id.coverage_template_id
            price = rec.laboratory_service_id.service_price_ids.filtered(
                lambda r: r.laboratory_code == cov.laboratory_code
            )
            cai = self.env["medical.coverage.agreement.item"].get_item(
                self.service_id, cov, self.laboratory_request_id.center_id
            )
            if (
                rec.laboratory_service_id.id
                in rec.laboratory_request_id.laboratory_service_ids.ids
            ):
                rec.is_sellable_insurance = False
                rec.is_sellable_private = False
                rec.coverage_amount = 0
                rec.coverage_cost = 0
                rec.private_amount = 0
                rec.private_cost = 0
            elif price and cai:
                rec.coverage_agreement_id = cai.coverage_agreement_id
                if cai.coverage_percentage > 0:
                    rec.is_sellable_insurance = True
                    rec.coverage_amount = price.amount * cai.coverage_percentage / 100
                    rec.coverage_cost = price.cost * cai.coverage_percentage / 100
                else:
                    rec.is_sellable_insurance = False
                    rec.coverage_cost = 0
                    rec.coverage_amount = 0
                if cai.coverage_percentage < 100:
                    rec.is_sellable_private = True
                    rec.private_amount = (
                        price.amount * (100 - cai.coverage_percentage) / 100
                    )
                    rec.private_cost = (
                        price.cost * (100 - cai.coverage_percentage) / 100
                    )
                else:
                    rec.is_sellable_private = False
                    rec.private_amount = 0
                    rec.private_cost = 0
            elif rec.laboratory_service_id:
                raise ValidationError(_("Laboratory service is not covered."))

    def _check_request(self):
        requests = self.laboratory_sample_id.encounter_id.laboratory_request_ids
        for request in requests.filtered(
            lambda r: r.state != "cancelled"
            and self.service_id in r.laboratory_service_ids
        ):
            return request
        return super(MedicalLaboratoryEvent, self)._check_request()
