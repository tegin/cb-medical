from odoo import fields, models


class InvoiceGroupMethod(models.Model):
    _name = "invoice.group.method"
    _description = "invoice.group.method"

    name = fields.Char(string="Invoice Group", required=True, translate=True)
