# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.AbstractModel):
    _inherit = "sale.order"

    encounter_id = fields.Many2one(
        "medical.encounter", readonly=True, index=True
    )
    coverage_id = fields.Many2one("medical.coverage", readonly=True)
    coverage_template_id = fields.Many2one(
        "medical.coverage.template",
        readonly=True,
        related="coverage_id.coverage_template_id",
    )
    coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement",
        index=True,
    )
    patient_id = fields.Many2one("medical.patient", readonly=True, index=True)
    patient_name = fields.Char(
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]}
    )
    subscriber_id = fields.Char(
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]}
    )
    invoice_group_method_id = fields.Many2one(
        "invoice.group.method", readonly=True, index=True
    )

    def create_third_party_move(self):
        if self.coverage_agreement_id:
            return
        return super().create_third_party_move()

    @api.model
    def _prepare_third_party_order(self):
        res = super(SaleOrder, self)._prepare_third_party_order()
        res["encounter_id"] = self.encounter_id.id or False
        res["patient_id"] = self.patient_id.id or False
        res["invoice_group_method_id"] = self.env.ref(
            "cb_medical_careplan_sale.third_party"
        ).id
        return res

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.encounter_id:
            res["is_medical"] = True
            if self.coverage_agreement_id:
                p = self.coverage_id.coverage_template_id
                res["show_patient"] = p.payor_id.show_patient
                res["show_subscriber"] = p.payor_id.show_subscriber
                res["show_authorization"] = p.payor_id.show_authorization
                res["coverage_template_id"] = p.id
            else:
                res["encounter_id"] = self.encounter_id.id
                res["coverage_template_id"] = False
        return res

    @api.model
    def sale_shared_fields(self):
        return ["patient_name", "subscriber_id"]

    def _get_invoice_grouping_keys(self):
        result = super()._get_invoice_grouping_keys()
        result.append("coverage_template_id")
        return result

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("not_sale_share_values", False):
            shared_vals = {}
            for key in self.sale_shared_fields():
                if key in vals:
                    shared_vals.update({key: vals[key]})
            if shared_vals:
                self.mapped("order_line").with_context(
                    not_sale_share_values=True
                ).write(shared_vals)
        return res
