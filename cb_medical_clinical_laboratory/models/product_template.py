# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"
    laboratory_request_ok = fields.Boolean(
        string="Can be requested to Laboratory"
    )
    laboratory_service_ids = fields.Many2many(
        comodel_name="product.template",
        relation="laboratory_product_template_child",
        column1="product_parent_id",
        column2="product_child_id",
        domain=[
            ("laboratory_request_ok", "=", True),
            ("type", "=", "service"),
        ],
    )
