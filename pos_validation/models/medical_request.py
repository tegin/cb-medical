# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    def get_sale_order_line_vals(self, is_insurance):
        vals = super().get_sale_order_line_vals(is_insurance)
        if is_insurance:
            vals["coverage_agreement_item_id"] = (
                self.coverage_agreement_item_id.id or False
            )
        return vals

    def _change_authorization(self, vals, **kwargs):
        res = super()._change_authorization(vals, **kwargs)
        if self.mapped("sale_order_line_ids"):
            self.mapped("sale_order_line_ids").filtered(
                lambda r: not r.is_private
            ).write(vals)
            for sale_line in self.mapped("sale_order_line_ids"):
                if (
                    sale_line.order_id.invoice_group_method_id
                    == sale_line.invoice_group_method_id
                ):
                    continue
                old_order = sale_line.order_id
                order = self.encounter_id.sale_order_ids.filtered(
                    lambda r: (
                        (
                            old_order.coverage_agreement_id
                            == r.coverage_agreement_id
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
                        or (
                            not old_order.third_party_order
                            and not r.third_party_order
                        )
                    )
                    and r.state == "draft"
                    and r.partner_id == old_order.partner_id
                    and r.invoice_group_method_id
                    == sale_line.invoice_group_method_id
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

    def cancel(self):
        lines = self.mapped("sale_order_line_ids")
        if any(order.state != "draft" for order in lines.mapped("order_id")):
            raise UserError(_("Cannot cancel validated lines"))
        res = super().cancel()
        lines.unlink()
        return res

    def cancel_values(self):
        vals = super().cancel_values()
        vals.update({"sale_order_line_ids": [(5,)]})
        return vals

    def _check_cancellable(self):
        if all(
            order.state == "draft"
            for order in self.mapped("sale_order_line_ids.order_id")
        ) and self.env.context.get("validation_cancel", False):
            return True
        return super()._check_cancellable()
