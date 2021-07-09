from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    bank_statement_line_ids = fields.One2many(
        "account.bank.statement.line", inverse_name="invoice_id", readonly=True
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    down_payment_line_id = fields.Many2one(
        "account.move.line", default=False, readonly=True, copy=False
    )
