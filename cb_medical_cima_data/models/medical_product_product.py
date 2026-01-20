# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalProductProduct(models.Model):

    _inherit = "medical.product.product"

    name_product_cima = fields.Char()
