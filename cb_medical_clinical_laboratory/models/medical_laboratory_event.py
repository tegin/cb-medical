# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalLaboratoryEvent(models.Model):
    _inherit = "medical.laboratory.event"

    delay = fields.Date()
    service_id = fields.Many2one(
        domain=[("laboratory_request_ok", "=", True), ("type", "=", "service")]
    )
    laboratory_code = fields.Char(
        readonly=True,
        store=True,
        compute="_compute_laboratory_code",
    )
    laboratory_service_ids = fields.Many2many(
        related="laboratory_request_id.laboratory_service_ids",
        string="Request Laboratory services",
    )
    # TODO: Remove this on the future
    cost = fields.Float(compute="_compute_is_sellable", store=True)
    private_cost = fields.Float(compute="_compute_is_sellable", store=True)
    coverage_cost = fields.Float(compute="_compute_is_sellable", store=True)

    @api.depends("performer_id", "service_id")
    def _compute_laboratory_code(self):
        for record in self:
            seller = record.service_id._select_seller(
                partner_id=record.performer_id
            )
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
            and self.service_id
            in self.laboratory_request_id._get_laboratory_services()
        ):
            return False
        return super(MedicalLaboratoryEvent, self)._get_is_billable()

    def _check_request(self):
        requests = (
            self.laboratory_sample_id.encounter_id.laboratory_request_ids
        )
        for request in requests.filtered(
            lambda r: r.state != "cancelled"
            and self.service_id in r._get_laboratory_services()
        ):
            return request
        return super(MedicalLaboratoryEvent, self)._check_request()

    @api.onchange("service_id")
    def _onchange_service(self):
        for rec in self:
            rec.name = rec.service_id.name
