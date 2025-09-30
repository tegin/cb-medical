# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueArea(models.Model):

    _name = "queue.area"
    _description = "Queue Area"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    location_ids = fields.One2many("queue.location.area", inverse_name="area_id")
    alias = fields.Char(
        help="Alias for the queue location area",
    )
    alias_2 = fields.Char(
        help="Alias 2 for the queue location area",
    )
