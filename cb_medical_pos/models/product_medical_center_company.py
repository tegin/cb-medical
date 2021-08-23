# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductMedicalCenterCompany(models.Model):

    _name = "product.medical.center.company"
    _description = "Product Template Medical Center Company"  # TODO

    product_tmpl_id = fields.Many2one("product.template", required=True)
    center_id = fields.Many2one(
        "res.partner",
        domain=[("is_medical", "=", True), ("is_center", "=", True)],
        required=True,
    )
    company_id = fields.Many2one("res.company")

    _sql_constraints = [
        (
            "product_medical_center_company_unique",
            "unique(product_tmpl_id, center_id)",
            "This product is already defined for this center",
        ),
    ]
