from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    encounter_final_invoice = fields.Boolean(readonly=True)
