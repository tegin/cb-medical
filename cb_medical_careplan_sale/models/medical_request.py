# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    @api.model
    def _get_sale_order_domain(self):
        return [("medical_model", "=", self._name)]

    sale_order_line_ids = fields.One2many(
        string="Sale order lines",
        comodel_name="sale.order.line",
        inverse_name="medical_res_id",
        domain=lambda self: self._get_sale_order_domain(),
    )
    sale_order_line_count = fields.Integer(compute="_compute_sale_order_line_count")
    is_sellable_insurance = fields.Boolean(compute="_compute_is_sellable")
    is_sellable_private = fields.Boolean(compute="_compute_is_sellable")
    sub_payor_id = fields.Many2one(
        "res.partner",
        domain="[('payor_id', '=', payor_id), ('is_sub_payor', '=', True)]",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    payor_id = fields.Many2one(
        "res.partner",
        related="coverage_id.coverage_template_id.payor_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    authorization_method_id = fields.Many2one(
        "medical.authorization.method", tracking=True, readonly=True
    )
    invoice_group_method_id = fields.Many2one(
        "invoice.group.method",
        string="Invoice Group Method",
        tracking=True,
        readonly=True,
    )
    qty = fields.Integer(
        default=1,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    medical_sale_discount_id = fields.Many2one("medical.sale.discount", readonly=True)
    discount = fields.Float(readonly=True, digits="Discount")

    @api.depends("sale_order_line_ids")
    def _compute_sale_order_line_count(self):
        for record in self:
            record.sale_order_line_count = len(record.sale_order_line_ids)

    def get_third_party_partner(self):
        return self.env["res.partner"]

    @api.onchange("coverage_id")
    def _onchange_coverage_id(self):
        for record in self:
            record.sub_payor_id = False

    @api.depends(
        "is_billable",
        "sale_order_line_ids",
        "coverage_agreement_item_id",
        "state",
    )
    def _compute_is_sellable(self):
        for rec in self:
            ca = rec.coverage_agreement_id
            rec.is_sellable_private = bool(
                rec.fhir_state not in ["cancelled"]
                and rec.is_billable
                and len(
                    rec.sale_order_line_ids.filtered(
                        lambda r: (
                            r.state != "cancel" and not r.order_id.coverage_agreement_id
                        )
                    )
                )
                == 0
                and rec.check_sellable(False, rec.coverage_agreement_item_id)
            )
            rec.is_sellable_insurance = bool(
                rec.fhir_state not in ["cancelled"]
                and rec.is_billable
                and len(
                    rec.sale_order_line_ids.filtered(
                        lambda r: (
                            r.state != "cancel"
                            and r.order_id.coverage_agreement_id.id == ca.id
                        )
                    )
                )
                == 0
                and rec.check_sellable(True, rec.coverage_agreement_item_id)
            )

    def check_sellable(self, is_insurance, agreement_item):
        if is_insurance:
            return agreement_item.coverage_sellable > 0
        return agreement_item.private_sellable > 0

    def compute_price(self, is_insurance):
        cai = (
            self.coverage_agreement_item_id
            or self.request_group_id.coverage_agreement_item_id
        )
        return cai.coverage_price if is_insurance else cai.private_price

    def get_sale_order_line_vals(self, is_insurance):
        res = {
            "product_id": self.service_id.id,
            "name": self.service_id.name or self.name,
            "medical_model": self._name,
            "medical_res_id": self.id,
            "product_uom_qty": self.qty or 1,
            "product_uom": self.service_id.uom_id.id,
            "price_unit": self.compute_price(is_insurance),
            "authorization_status": self.authorization_status,
            "encounter_id": self.encounter_id.id or False,
        }
        if is_insurance:
            res["invoice_group_method_id"] = self.invoice_group_method_id.id
            res["authorization_method_id"] = self.authorization_method_id.id
            res["patient_name"] = self.patient_id.display_name
            res["authorization_number"] = self.authorization_number
            res["subscriber_id"] = self.coverage_id.subscriber_id
        if self.medical_sale_discount_id:
            res["discount"] = self.discount or 0.0
            res["medical_sale_discount_id"] = self.medical_sale_discount_id.id
        return res

    def check_is_billable(self):
        if self.is_billable:
            return True
        # Agreement is researched if it is not billable
        self.coverage_agreement_item_id = self.env[
            "medical.coverage.agreement.item"
        ].get_item(
            self.service_id,
            self.coverage_id.coverage_template_id,
            self.center_id,
        )
        if not self.coverage_agreement_item_id:
            raise ValidationError(_("Agreement must be defined"))
        return self.is_billable

    def breakdown(self):
        self.ensure_one()
        if not self.is_billable or not self.is_breakdown:
            raise ValidationError(_("Cannot breakdown a not billable line"))
        if self.sale_order_line_ids:
            raise ValidationError(
                _("Sale order is created. " "It must be deleted in order to breakdown")
            )
        self.is_billable = False
        self.is_breakdown = False
        for model in self._get_request_models():
            requests = self.env[model].search(
                [
                    ("parent_model", "=", self._name),
                    ("parent_id", "=", self.id),
                ]
            )
            for request in requests:
                if not request.check_is_billable():
                    request.is_billable = True

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
            self.careplan_id.coverage_id
            if is_insurance
            else self.careplan_id.coverage_id.browse(),
            self.get_third_party_partner(),
            self.invoice_group_method_id
            if is_insurance
            else self.invoice_group_method_id.browse(),
        )

    def _get_sale_order_partner(self, is_insurance=False):
        if is_insurance:
            return self.careplan_id.get_payor()
        return self.encounter_id.get_patient_partner()

    def get_sale_order_query(self):
        query = []
        fieldname = self._get_parent_field_name()
        request_models = self._get_request_models()
        for request in self.filtered(lambda r: r.fhir_state not in ["cancelled"]):
            if request.is_sellable_insurance:
                query.append(request._get_sale_order_query_vals(True))
            if request.is_sellable_private:
                query.append(request._get_sale_order_query_vals(False))
            for model in request_models:
                childs = self.env[model].search(
                    [
                        (fieldname, "=", request.id),
                        ("parent_id", "=", request.id),
                        ("parent_model", "=", request._name),
                        ("fhir_state", "!=", "cancelled"),
                    ]
                )
                query += childs.get_sale_order_query()
        return query

    def _update_related_activity(self, vals, parent, plan, action):
        # TODO: Review
        res = super()._update_related_activity(vals, parent, plan, action)
        if self.encounter_id.state in ["onleave", "finished"]:
            if not self.sale_order_line_ids and self.is_billable:
                # TODO: What should happen? We should create if possible
                pass
            for _line in self.sale_order_line_ids:
                # TODO: Review it according to their configuration .
                # (Insurance / Private)
                pass
        return res
