# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueLocationGroup(models.Model):

    _inherit = "queue.location.group"

    color = fields.Char()
