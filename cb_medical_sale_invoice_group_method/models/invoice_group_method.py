from odoo import fields, models


class InvoiceGroupMethod(models.Model):
    _inherit = 'invoice.group.method'

    invoice_by_preinvoice = fields.Boolean()
    no_invoice = fields.Boolean()
