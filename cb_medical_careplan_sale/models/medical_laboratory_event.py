# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


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
    coverage_amount = fields.Float(required=True, default=0)
    private_amount = fields.Float(required=True, default=0)
    is_sellable_insurance = fields.Boolean(required=True, default=False)
    is_sellable_private = fields.Boolean(required=True, default=False)
    authorization_status = fields.Selection(
        [
            ("pending", "Pending authorization"),
            ("not-authorized", "Not authorized"),
            ("authorized", "Authorized"),
        ],
        readonly=True,
    )
    coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement", readonly=False, ondelete="restrict"
    )
    invoice_group_method_id = fields.Many2one(
        string="Invoice Group Method",
        comodel_name="invoice.group.method",
        tracking=True,
        readonly=True,
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
            self.invoice_group_method_id,
        )

    def _get_sale_order_partner(self, is_insurance=False):
        if is_insurance:
            return self.laboratory_request_id.careplan_id.get_payor()
        return self.laboratory_request_id.encounter_id.get_patient_partner()

    def get_sale_order_query(self):
        query = []
        for request in self.filtered(lambda r: r.state not in ["aborted"]):
            if request.is_sellable_insurance and request.coverage_amount > 0:
                query.append(request._get_sale_order_query_vals(True))
            if request.is_sellable_private and request.private_amount > 0:
                query.append(request._get_sale_order_query_vals(False))
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
            "encounter_id": self.encounter_id.id or False,
        }
        if is_insurance:
            res["invoice_group_method_id"] = self.invoice_group_method_id.id
            res["patient_name"] = self.patient_id.display_name
            res[
                "authorization_number"
            ] = self.laboratory_request_id.authorization_number
            res["subscriber_id"] = self.laboratory_request_id.coverage_id.subscriber_id
        return res

    def compute_price(self, is_insurance):
        return self.coverage_amount if is_insurance else self.private_amount
