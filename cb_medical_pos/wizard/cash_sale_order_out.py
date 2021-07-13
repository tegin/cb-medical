# Copyright (C) 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools import float_is_zero


class CashSaleOrderOut(models.TransientModel):
    _name = "cash.sale.order.out"
    _inherit = "cash.box.out"
    _description = "Pos Cash Box a Third party Sale Order"

    session_id = fields.Many2one("pos.session", required=True)
    sale_order_id = fields.Many2one(
        "sale.order", string="Sale Order", required=True
    )
    name = fields.Char(related="sale_order_id.name", readonly=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="session_id.company_id",
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="session_id.currency_id",
        required=True,
        readonly=True,
    )
    payment_method_ids = fields.Many2many(
        comodel_name="pos.payment.method",
        related="session_id.payment_method_ids",
        string="Payment methods",
    )
    payment_method_id = fields.Many2one(
        comodel_name="pos.payment.method",
        required=True,
        default=lambda self: self._default_payment_method(),
    )
    payment_method_count = fields.Integer(
        compute="_compute_payment_method_count", readonly=True,
    )

    @api.depends("payment_method_ids")
    def _compute_payment_method_count(self):
        for record in self:
            record.payment_method_count = len(record.payment_method_ids)

    @api.onchange("sale_order_id")
    def _onchange_sale_order(self):
        if self.sale_order_id:
            self.amount = self.sale_order_id.residual

    def _run_order_vals(self):
        return {
            "amount_total": self.amount,
            "currency_id": self.currency_id.id,
            "partner_id": self.sale_order_id.partner_id.id,
            "sale_order_id": self.sale_order_id.id,
            "session_id": self.session_id.id,
            "amount_tax": 0,
            "amount_paid": self.amount,
            "amount_return": 0,
            "account_move": self.sale_order_id.third_party_move_id.id,
        }

    def run(self):
        if not float_is_zero(
            self.amount, precision_rounding=self.currency_id.rounding
        ):
            order = self.env["pos.order"].create(self._run_order_vals())
            order.add_payment(
                {
                    "pos_order_id": order.id,
                    "amount": order._get_rounded_amount(self.amount),
                    "name": self.sale_order_id.name,
                    "payment_method_id": self.payment_method_id.id,
                }
            )
            order.action_pos_order_paid()
            order.state = "invoiced"
        return
