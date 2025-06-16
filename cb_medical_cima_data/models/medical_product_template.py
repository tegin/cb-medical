# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalProductTemplate(models.Model):

    _inherit = "medical.product.template"

    name_template_cima = fields.Char()

    def name_get(self):
        return [(rec.id, rec.name_template_cima or "") for rec in self]
