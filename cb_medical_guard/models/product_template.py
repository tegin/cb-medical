# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    is_guard = fields.Boolean()
    is_invoiceable_guard = fields.Boolean(string="Invoiceable Guard")
