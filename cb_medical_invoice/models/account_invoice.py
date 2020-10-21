from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    encounter_final_invoice = fields.Boolean(readonly=True)

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            partner = invoice.partner_id
            if (
                partner.self_invoice
                and invoice.type in "in_refund"
                and invoice.set_self_invoice
            ):
                sequence = partner.self_invoice_refund_sequence_id
                invoice.self_invoice_number = sequence.with_context(
                    ir_sequence_date=invoice.date
                ).next_by_id()
        return res
