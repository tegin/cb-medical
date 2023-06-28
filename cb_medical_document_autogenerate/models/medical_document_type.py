# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDocumentType(models.Model):
    _inherit = "medical.document.type"

    kind = fields.Selection(
        [
            ("administrative", "Administrative"),
            ("medical", "Medical"),
        ],
        default="administrative",
    )
