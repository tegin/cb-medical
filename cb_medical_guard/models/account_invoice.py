from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    guard_id = fields.Many2one("medical.guard", ondelete="restrict")
