# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    prescription_default_center_id = fields.Many2one(
        "res.partner",
        domain=[("is_center", "=", True)],
        string="Default center in prescription",
        config_parameter="cb.prescription_default_center_id",
    )
