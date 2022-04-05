# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LaboratoryEvent(models.Model):
    _inherit = "medical.laboratory.event"

    @api.model
    def _get_sale_order_domain(self):
        return [("medical_model", "=", self._name)]

    sale_order_line_ids = fields.One2many(
        string="Sale order lines",
        comodel_name="sale.order.line",
        inverse_name="medical_res_id",
        domain=lambda self: self._get_sale_order_domain(),
    )
    # We keep as stored in order to keep old data correctly
    coverage_amount = fields.Float(compute="_compute_is_sellable", store=True)
    private_amount = fields.Float(compute="_compute_is_sellable", store=True)
    is_sellable_insurance = fields.Boolean(
        compute="_compute_is_sellable", store=True
    )
    is_sellable_private = fields.Boolean(
        compute="_compute_is_sellable", store=True
    )
    authorization_status = fields.Selection(
        [
            ("pending", "Pending authorization"),
            ("not-authorized", "Not authorized"),
            ("authorized", "Authorized"),
        ],
        readonly=True,
    )
    coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement",
        readonly=False,
        ondelete="restrict",
        compute="_compute_is_sellable",
        store=True,
    )
    coverage_agreement_item_id = fields.Many2one(
        "medical.coverage.agreement.item",
        readonly=True,
        ondelete="restrict",
        compute="_compute_is_sellable",
        store=True,
    )
    invoice_group_method_id = fields.Many2one(
        string="Invoice Group Method",
        comodel_name="invoice.group.method",
        readonly=True,
        related="laboratory_request_id.invoice_group_method_id",
    )
    is_billable = fields.Boolean(
        compute="_compute_is_sellable",
        store=True,
        string="Is billable?",
        default=True,
        tracking=True,
    )

    def _get_sale_order_query_vals(self, is_insurance=False):
        partner = self._get_sale_order_partner(is_insurance=is_insurance)
        return (
            self.with_context(
                lang=partner.lang or self.env.user.lang
            ).get_sale_order_line_vals(is_insurance),
            self.coverage_agreement_id
            if is_insurance
            else self.coverage_agreement_id.browse(),
            partner,
            self.laboratory_request_id.careplan_id.coverage_id
            if is_insurance
            else self.laboratory_request_id.careplan_id.coverage_id.browse(),
            self.laboratory_request_id.get_third_party_partner(),
            self.invoice_group_method_id
            if is_insurance
            else self.env["invoice.group.method"],
        )

    def _get_sale_order_partner(self, is_insurance=False):
        if is_insurance:
            return self.laboratory_request_id.careplan_id.get_payor()
        return self.laboratory_request_id.encounter_id.get_patient_partner()

    def get_sale_order_query(self):
        query = []
        for event in self.filtered(lambda r: r.state not in ["aborted"]):
            if event.is_sellable_insurance and event.coverage_amount > 0:
                query.append(event._get_sale_order_query_vals(True))
            if event.is_sellable_private and event.private_amount > 0:
                query.append(event._get_sale_order_query_vals(False))
        return query

    def get_sale_order_line_vals(self, is_insurance):
        res = {
            "product_id": self.service_id.id,
            "name": self.name or self.service_id.name,
            # "laboratory_event_id": self.id,
            "medical_model": self._name,
            "medical_res_id": self.id,
            "product_uom_qty": 1,
            "product_uom": self.service_id.uom_id.id,
            "price_unit": self.compute_price(is_insurance),
            "authorization_status": self.authorization_status,
            "encounter_id": self.laboratory_sample_id.encounter_id.id or False,
        }
        if is_insurance:
            res["invoice_group_method_id"] = self.invoice_group_method_id.id
            res["patient_name"] = self.patient_id.display_name
            res[
                "authorization_number"
            ] = self.laboratory_request_id.authorization_number
            res[
                "subscriber_id"
            ] = self.laboratory_request_id.coverage_id.subscriber_id
        return res

    def compute_price(self, is_insurance):
        return self.coverage_amount if is_insurance else self.private_amount

    def check_sellable(self, is_insurance, agreement_item):
        if is_insurance:
            return agreement_item.coverage_sellable > 0
        return agreement_item.private_sellable > 0

    def _get_is_billable(self):
        # In some case, we might want to force it to be not billable
        return True

    @api.depends(
        "is_billable",
        "sale_order_line_ids",
        "laboratory_request_id",
        "service_id",
        "state",
    )
    def _compute_is_sellable(self):
        for rec in self:
            rec._compute_sellable_fields()

    def _compute_sellable_fields(self):
        self.is_billable = self._get_is_billable()
        if not self.laboratory_request_id or not self.is_billable:
            self.coverage_agreement_id = False
            self.coverage_agreement_item_id = False
            self.is_sellable_private = self.is_billable
            self.is_sellable_insurance = self.is_billable
            self.coverage_amount = 0
            self.private_amount = 0
            return
        cai = self.env["medical.coverage.agreement.item"].get_item(
            self.service_id,
            self.laboratory_request_id.coverage_id.coverage_template_id,
            self.laboratory_sample_id.center_id,
        )
        if not cai:
            raise ValidationError(_("Agreement must be defined"))

        ca = cai.coverage_agreement_id
        self.coverage_agreement_item_id = cai
        self.coverage_agreement_id = ca
        self.is_sellable_private = bool(
            self.state not in ["cancelled"]
            and self.is_billable
            and len(
                self.sale_order_line_ids.filtered(
                    lambda r: (
                        r.state != "cancel"
                        and not r.order_id.coverage_agreement_id
                    )
                )
            )
            == 0
            and self.check_sellable(False, self.coverage_agreement_item_id)
        )
        self.is_sellable_insurance = bool(
            self.state not in ["cancelled"]
            and self.is_billable
            and len(
                self.sale_order_line_ids.filtered(
                    lambda r: (
                        r.state != "cancel"
                        and r.order_id.coverage_agreement_id.id == ca.id
                    )
                )
            )
            == 0
            and self.check_sellable(True, self.coverage_agreement_item_id)
        )
        self.coverage_amount = cai.coverage_price
        self.private_amount = cai.private_price

    def _check_requests(self):
        force_change = self.env.context.get("force_check_request")
        for event in self:
            if event.sale_order_line_ids or (
                event.laboratory_request_id and not force_change
            ):
                continue
            event.laboratory_request_id = event._check_request()
            if event.laboratory_request_id:
                group = event.laboratory_request_id.request_group_id
                wizard = (
                    self.env["medical.request.group.check.authorization"]
                    .with_context(default_request_group_id=group.id)
                    .create(
                        {
                            "authorization_method_id": group.authorization_method_id.id,
                            "authorization_number": group.authorization_number,
                        }
                    )
                )
                wizard.run()

    def _check_request(self):
        for (
            request
        ) in self.laboratory_sample_id.encounter_id.laboratory_request_ids.filtered(
            lambda r: r.state != "cancelled"
        ).sorted(
            "coverage_percentage", reverse=True
        ):
            if self.env["medical.coverage.agreement.item"].get_item(
                self.service_id,
                request.coverage_id.coverage_template_id,
                self.laboratory_sample_id.center_id,
            ):
                return request
        return False

    @api.model_create_multi
    def create(self, mvals):
        result = super(LaboratoryEvent, self).create(mvals)
        result._check_requests()
        return result
