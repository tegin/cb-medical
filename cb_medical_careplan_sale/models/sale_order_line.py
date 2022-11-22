# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    encounter_id = fields.Many2one("medical.encounter", readonly=True, index=True)
    medical_model = fields.Char(index=True)
    medical_res_id = fields.Many2oneReference(index=True, model_field="medical_model")
    invoice_group_method_id = fields.Many2one(
        "invoice.group.method", readonly=True, index=True
    )
    authorization_method_id = fields.Many2one(
        "medical.authorization.method",
        tracking=True,
        readonly=True,
        index=True,
    )
    authorization_checked = fields.Boolean(default=False, readonly=True)
    authorization_status = fields.Selection(
        [
            ("pending", "Pending authorization"),
            ("not-authorized", "Not authorized"),
            ("authorized", "Authorized"),
        ],
        readonly=True,
    )
    medical_sale_discount_id = fields.Many2one("medical.sale.discount", readonly=True)
    authorization_number = fields.Char()
    subscriber_id = fields.Char()
    patient_name = fields.Char()
    coverage_template_id = fields.Many2one(
        "medical.coverage.template",
        related="order_id.coverage_id.coverage_template_id",
    )

    def _prepare_third_party_order_line(self):
        res = super()._prepare_third_party_order_line()
        res["invoice_group_method_id"] = self.env.ref(
            "cb_medical_careplan_sale.third_party"
        ).id
        res["encounter_id"] = self.encounter_id.id or False
        res["authorization_number"] = self.authorization_number or False
        res["subscriber_id"] = self.subscriber_id or False
        res["patient_name"] = self.patient_name or False
        return res

    def open_medical_record(self):
        action = {
            "name": _("Medical Record"),
            "type": "ir.actions.act_window",
            "res_model": self.medical_model,
            "res_id": self.medical_res_id,
            "view_mode": "form",
        }
        return action

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("not_sale_share_values", False):
            shared_vals = {}
            for key in self.env["sale.order"].sale_shared_fields():
                if key in vals:
                    shared_vals.update({key: vals[key]})
            if shared_vals:
                self.mapped("order_id").with_context(not_sale_share_values=True).write(
                    shared_vals
                )
                self.mapped("order_id").mapped("order_line").filtered(
                    lambda r: r not in self
                ).with_context(not_sale_share_values=True).write(shared_vals)
        return res

    def _prepare_invoice_line(self):
        res = super()._prepare_invoice_line()
        if self.encounter_id:
            res["patient_name"] = self.patient_name
            res["subscriber_id"] = self.subscriber_id
            res["encounter_id"] = self.encounter_id.id
            res["authorization_number"] = self.authorization_number
            agreement = self.order_id.coverage_agreement_id
            if agreement:
                # TODO: Pass this to cb_facturae
                # if agreement.file_reference:
                #     res["facturae_file_reference"] = agreement.file_reference
                if agreement.discount and agreement.discount > 0.0:
                    res["discount"] = agreement.discount
        if self.coverage_template_id:
            nomenc = self.coverage_template_id.payor_id.invoice_nomenclature_id
            if nomenc:
                item = nomenc.item_ids.filtered(
                    lambda r: r.product_id == self.product_id
                )
                if item:
                    res["name"] = item.name
        return res
