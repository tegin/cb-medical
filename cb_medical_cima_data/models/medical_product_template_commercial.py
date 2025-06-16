# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalProductTemplateCommercial(models.Model):

    _inherit = "medical.product.template.commercial"

    # Type 1: Ficha Técnica (FT) pdf link
    ft_pdf_link = fields.Char(
        string="Data sheet PDF",
    )
    # Type 2: Prospecto (P)
    prospect_pdf_link = fields.Char(
        string="Prospect PDF",
    )
    # Type 3: Informe Público Europeo de Evaluación (IPE)
    ipe_pdf_link = fields.Char(
        string="European Public Assessment Report PDF",
    )

    name_cima = fields.Char()

    def name_get(self):
        return [(rec.id, rec.name_cima or "") for rec in self]
