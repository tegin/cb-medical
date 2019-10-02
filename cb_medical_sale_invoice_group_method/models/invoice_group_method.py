from odoo import fields, models


class InvoiceGroupMethod(models.Model):
    _inherit = "invoice.group.method"

    invoice_by_preinvoice = fields.Boolean()
    no_invoice = fields.Boolean()
    third_party = fields.Boolean()

    def get_journal(self, company):
        self.ensure_one()
        if self.third_party:
            return company.third_party_sale_journal_id
        return self.env["account.journal"]
