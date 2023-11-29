# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pos_session_id = fields.Many2one(
        comodel_name="pos.session", string="PoS Session", readonly=1
    )
    is_down_payment = fields.Boolean(default=False)
    account_id = fields.Many2one(comodel_name="account.account", readonly=True)
    pos_order_ids = fields.One2many("pos.order", inverse_name="sale_order_id")

    def create_third_party_move(self):
        res = super().create_third_party_move()
        self.account_id = self.partner_id.with_company(
            self.company_id.id
        ).property_third_party_customer_account_id
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    down_payment_line_id = fields.Many2one(
        "account.move.line",
        default=False,
        readonly=True,
        copy=False,
        index=True,
    )
    down_payment_sale_line_id = fields.Many2one(
        "sale.order.line", default=False, readonly=True, copy=False, index=True
    )

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if self.down_payment_line_id:
            res["down_payment_line_id"] = self.down_payment_line_id.id
        return res

    def _get_invoice_name(self):
        return "{} ({})".format(self.invoice_lines[0].move_id.name, self.name)
