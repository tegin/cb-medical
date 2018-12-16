from odoo import fields, models


class InvoiceGroupMethod(models.Model):
    _inherit = 'invoice.group.method'

    invoice_at_validation = fields.Boolean()
