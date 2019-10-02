# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = "product.category"

    category_product_id = fields.Many2one(
        "product.product", domain=[("type", "=", "service")]
    )

    @api.constrains("category_product_id")
    def _check_category_product(self):
        for rec in self.filtered(lambda r: r.category_product_id):
            if rec.category_product_id.type != "service":
                raise ValidationError(
                    _("Category product must be always a service")
                )
