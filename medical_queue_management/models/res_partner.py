# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    queue_location_ids = fields.One2many(
        "res.partner.queue.location", inverse_name="practitioner_id"
    )
