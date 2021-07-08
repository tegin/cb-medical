# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    preinvoice_status = fields.Selection(
        [
            ("draft", "Draft"),
            ("to preinvoice", "To Prenvoice"),
            ("preinvoiced", "Prenvoiced"),
        ],
        store=True,
        compute="_compute_preinvoice_status",
    )

    @api.depends(
        "state",
        "order_line.invoice_status",
        "third_party_order",
        "order_line.invoice_group_method_id",
        "order_line.invoice_group_method_id.invoice_by_preinvoice",
        "order_line.qty_invoiced",
        "order_line.product_uom_qty",
        "order_line.preinvoice_group_id",
    )
    def _compute_preinvoice_status(self):
        for order in self:
            if order.state not in ["draft", "cancel"]:
                if order.third_party_order or all(
                    line.preinvoice_group_id
                    for line in order.order_line.filtered(
                        lambda r: r.invoice_group_method_id.invoice_by_preinvoice
                        or r.qty_invoiced == r.product_uom_qty
                    )
                ):
                    order.preinvoice_status = "preinvoiced"
                else:
                    order.preinvoice_status = "to preinvoice"
            else:
                order.preinvoice_status = "draft"

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.encounter_id and self.coverage_agreement_id:
            res["agreement_id"] = self.coverage_agreement_id.id
            res["invoice_group_method_id"] = self.invoice_group_method_id.id
        return res
