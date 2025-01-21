# Copyright 2025 Dixmit
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class Commission(models.Model):
    _inherit = "commission"

    commission_type = fields.Selection(
        selection_add=[("medical", "Medical")], ondelete={"medical": "set default"}
    )
