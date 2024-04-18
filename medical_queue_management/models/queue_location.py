# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueLocation(models.Model):

    _inherit = "queue.location"

    action_ids = fields.Many2many("queue.location.action")
    allows_flag = fields.Boolean()
