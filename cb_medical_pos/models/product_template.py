# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    medical_center_company_ids = fields.One2many(
        "product.medical.center.company",
        inverse_name="product_tmpl_id",
    )
