from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    show_patient = fields.Boolean()
    show_subscriber = fields.Boolean()
    show_authorization = fields.Boolean()
    invoice_nomenclature_id = fields.Many2one(
        "product.nomenclature",
        "Nomenclature",
        help="Nomenclature for invoices",
    )
