# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueLocation(models.Model):

    _inherit = "queue.location"

    action_ids = fields.Many2many("queue.location.action")
    allows_flag = fields.Boolean()
    alias = fields.Char(
        help="Alias for the queue location, used in the zpl labels.",
    )
    alias_2 = fields.Char(
        help="Alias 2 for the queue location, used in the zpl labels.",
    )
