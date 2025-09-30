# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueLocationGroup(models.Model):

    _inherit = "queue.location.group"

    color = fields.Char()
    alias = fields.Char(
        help="Alias for the queue location group, used in the zpl labels.",
    )
    alias_2 = fields.Char(
        help="Alias 2 for the queue location group, used in the zpl labels.",
    )
