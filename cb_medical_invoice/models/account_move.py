from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    encounter_final_invoice = fields.Boolean(readonly=True)

    def _post(self, soft=True):
        # Set today for invoice date in self invoices
        self.filtered(
            lambda inv: inv.is_purchase_document(False)
            and inv.set_self_invoice
            and not inv.invoice_date
        ).invoice_date = fields.Date.today()
        res = super()._post(soft=soft)
        for invoice in self:
            partner = invoice.with_company(
                invoice.company_id or self.env.company,
            ).partner_id
            if (
                partner.self_invoice
                and invoice.is_purchase_document(False)
                and invoice.set_self_invoice
                and not invoice.self_invoice_number
            ):
                self_invoice_number = partner._get_self_invoice_number(invoice.date)
                invoice.ref = self_invoice_number
                invoice.self_invoice_number = self_invoice_number
        return res
