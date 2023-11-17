# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerQueueLocation(models.Model):

    _name = "res.partner.queue.location"
    _description = "Partner Queue Location"

    practitioner_id = fields.Many2one("res.partner", required=True)
    center_id = fields.Many2one("res.partner", domain=[("is_center", "=", True)])
    location_id = fields.Many2one("queue.location")
    group_id = fields.Many2one("queue.location.group")

    _sql_constraints = [
        (
            "center_area_uniq",
            "UNIQUE(practioner_id, center_id)",
            "Center for each area must be unique!",
        ),
    ]
