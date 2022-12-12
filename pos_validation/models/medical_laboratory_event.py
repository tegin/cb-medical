# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalLaboratoryEvent(models.Model):
    _inherit = "medical.laboratory.event"

    def get_sale_order_line_vals(self, is_insurance):
        vals = super().get_sale_order_line_vals(is_insurance)
        if is_insurance:
            cov = (
                self.laboratory_request_id.careplan_id.coverage_id.coverage_template_id
            )
            vals["coverage_agreement_item_id"] = (
                self.env["medical.coverage.agreement.item"]
                .get_item(self.service_id, cov, self.laboratory_request_id.center_id)
                .id
            )
        return vals

    def _change_authorization(self, vals, **kwargs):
        res = super()._change_authorization(vals, **kwargs)
        so_lines = self.mapped("sale_order_line_ids")
        if so_lines:
            new_vals = {}
            for key in vals:
                if key in so_lines._fields:
                    new_vals[key] = vals[key]
            so_lines.filtered(lambda r: not r.is_private).write(new_vals)
            for sale_line in so_lines:
                if (
                    sale_line.order_id.invoice_group_method_id
                    == sale_line.invoice_group_method_id
                ):
                    continue
                old_order = sale_line.order_id
                order = self.encounter_id.sale_order_ids.filtered(
                    lambda r: (
                        (
                            old_order.coverage_agreement_id == r.coverage_agreement_id
                            and old_order.coverage_agreement_id
                            and r.coverage_id == old_order.coverage_id
                        )
                        or (
                            not old_order.coverage_agreement_id
                            and not r.coverage_agreement_id
                        )
                    )
                    and (
                        (
                            sale_line.order_id.third_party_order
                            and r.third_party_order
                            and r.third_party_partner_id
                            == old_order.third_party_partner_id
                        )
                        or (not old_order.third_party_order and not r.third_party_order)
                    )
                    and r.state == "draft"
                    and r.partner_id == old_order.partner_id
                    and r.invoice_group_method_id == sale_line.invoice_group_method_id
                )
                if not order:
                    vals = self.encounter_id._get_sale_order_vals(
                        partner=old_order.partner_id,
                        coverage=old_order.coverage_id,
                        agreement=old_order.coverage_agreement_id,
                        third_party_partner=old_order.third_party_partner_id,
                        invoice_group_method=sale_line.invoice_group_method_id,
                    )
                    order = (
                        self.env["sale.order"]
                        .with_context(force_company=vals.get("company_id"))
                        .create(vals)
                    )
                    order.onchange_partner_id()
                sale_line.order_id = order
        return res
