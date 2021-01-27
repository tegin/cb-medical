# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    sale_order_line_ids = fields.One2many(
        string="Sale order lines",
        comodel_name="sale.order.line",
        compute="_compute_sale_order_line_ids",
    )
    is_sellable_insurance = fields.Boolean(compute="_compute_is_sellable")
    is_sellable_private = fields.Boolean(compute="_compute_is_sellable")
    sub_payor_id = fields.Many2one(
        "res.partner",
        domain="[('payor_id', '=', payor_id), ('is_sub_payor', '=', True)]",
    )
    payor_id = fields.Many2one(
        "res.partner",
        related="coverage_id.coverage_template_id.payor_id",
        readonly=True,
    )
    authorization_method_id = fields.Many2one(
        "medical.authorization.method", track_visibility=True, readonly=True
    )
    invoice_group_method_id = fields.Many2one(
        "invoice.group.method",
        string="Invoice Group Method",
        track_visibility=True,
        readonly=True,
    )
    qty = fields.Integer(default=1, required=True)

    def get_third_party_partner(self):
        return False

    def _compute_sale_order_line_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            rec.sale_order_line_ids = self.env["sale.order.line"].search(
                [(inverse_field_name, "=", rec.id)]
            )

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
                rec.state not in ["cancelled"]
                and rec.is_billable
                and len(
                    rec.sale_order_line_ids.filtered(
                        lambda r: (
                            r.state != "cancel"
                            and not r.order_id.coverage_agreement_id
                        )
                    )
                )
                == 0
                and rec.check_sellable(False, rec.coverage_agreement_item_id)
            )
            rec.is_sellable_insurance = bool(
                rec.state not in ["cancelled"]
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
            self._get_parent_field_name(): self.id,
            "product_uom_qty": self.qty or 1,
            "product_uom": self.service_id.uom_id.id,
            "price_unit": self.compute_price(is_insurance),
            "authorization_status": self.authorization_status,
            "encounter_id": self.encounter_id.id or False,
        }
        if is_insurance:
            res["invoice_group_method_id"] = self.invoice_group_method_id.id
            res["authorization_method_id"] = self.authorization_method_id.id
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

    @api.multi
    def breakdown(self):
        self.ensure_one()
        if not self.is_billable or not self.is_breakdown:
            raise ValidationError(_("Cannot breakdown a not billable line"))
        if self.sale_order_line_ids:
            raise ValidationError(
                _(
                    "Sale order is created. "
                    "It must be deleted in order to breakdown"
                )
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

    @api.multi
    def get_sale_order_query(self):
        query = []
        fieldname = self._get_parent_field_name()
        request_models = self._get_request_models()
        for request in self.filtered(lambda r: r.state not in ["cancelled"]):
            if request.is_sellable_insurance:
                query.append(
                    (
                        request.coverage_agreement_id.id,
                        request.careplan_id.get_payor(),
                        request.coverage_id.id,
                        True,
                        request.get_third_party_partner()
                        if request.third_party_bill
                        else 0,
                        request,
                    )
                )
            if request.is_sellable_private:
                query.append(
                    (
                        0,
                        request.encounter_id.get_patient_partner(),
                        False,
                        False,
                        request.get_third_party_partner()
                        if request.third_party_bill
                        else 0,
                        request,
                    )
                )
            for model in request_models:
                childs = self.env[model].search(
                    [
                        (fieldname, "=", request.id),
                        ("parent_id", "=", request.id),
                        ("parent_model", "=", request._name),
                        ("state", "!=", "cancelled"),
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
