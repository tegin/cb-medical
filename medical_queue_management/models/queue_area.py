# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueArea(models.Model):

    _name = "queue.area"
    _description = "Queue Area"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    location_ids = fields.One2many("queue.location.area", inverse_name="area_id")
