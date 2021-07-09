# Copyright (C) 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CashSaleOrderOut(models.TransientModel):
    _name = "cash.sale.order.out"
    _inherit = "cash.box.out"

    pos_session_id = fields.Many2one("pos.session", required=True)
    sale_order_id = fields.Many2one(
        "sale.order", string="Sale Order", required=True
    )
    name = fields.Char(related="sale_order_id.name", readonly=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="pos_session_id.company_id",
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="pos_session_id.currency_id",
        required=True,
        readonly=True,
    )
    payment_method_ids = fields.Many2many(
        comodel_name="pos.payment.method",
        related="pos_session_id.payment_method_ids",
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
    def _onchange_invoice(self):
        if self.sale_order_id:
            self.amount = self.sale_order_id.residual

    def _calculate_values_for_statement_line(self, record):
        res = super()._calculate_values_for_statement_line(record)
        res["sale_order_id"] = self.sale_order_id.id
        res["ref"] = self.sale_order_id.name
        res["partner_id"] = self.sale_order_id.partner_id.id
        return res

    def run(self):
        active_model = self.env.context.get("active_model", False)
        active_ids = self.env.context.get("active_ids", False)
        if active_model == "pos.session":
            bank_statements = [
                session.statement_ids.filtered(
                    lambda r: r.payment_method_id.id
                    == self.payment_method_id.id
                )
                for session in self.env[active_model].browse(active_ids)
            ]
            if not bank_statements:
                raise UserError(_("Bank Statement was not found"))
            return self._run(bank_statements)
        else:
            return super().run()
