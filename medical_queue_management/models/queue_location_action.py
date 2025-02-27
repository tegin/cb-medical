# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueLocationAction(models.Model):

    _name = "queue.location.action"
    _description = "Queue Location Action"  # TODO
    _order = "sequence asc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    sequence = fields.Integer()
    name = fields.Char()
    icon = fields.Char(string="Queue Icon")
    color = fields.Char()
