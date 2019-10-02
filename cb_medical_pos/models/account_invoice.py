from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    bank_statement_line_ids = fields.One2many(
        "account.bank.statement.line", inverse_name="invoice_id", readonly=True
    )


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    down_payment_line_id = fields.Many2one(
        "account.invoice.line", default=False, readonly=True, copy=False
    )
