# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueLocationArea(models.Model):
    _name = "queue.location.area"
    _description = "Location Area"

    area_id = fields.Many2one("queue.area", required=True)
    center_id = fields.Many2one(
        "res.partner", domain=[("is_center", "=", True)], required=True
    )
    location_id = fields.Many2one("queue.location")
    group_id = fields.Many2one("queue.location.group")

    _sql_constraints = [
        (
            "center_area_uniq",
            "UNIQUE(area_id, center_id)",
            "Center for each area must be unique!",
        ),
    ]
