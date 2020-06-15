from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    description_quote = fields.Text(
        "Quote Description",
        translate=True,
        help="A description of the Product that you want to communicate "
        "on your quotes",
    )
