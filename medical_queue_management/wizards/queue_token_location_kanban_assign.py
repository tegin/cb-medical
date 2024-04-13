# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueTokenLocationKanbanAssign(models.TransientModel):

    _name = "queue.token.location.kanban.assign"

    token_location_id = fields.Many2one("queue.token.location", required=True)
    group_id = fields.Many2one(related="token_location_id.group_id")
    location_id = fields.Many2one("queue.location", required=True)

    def assign(self):
        self.token_location_id.with_context(
            location_id=self.location_id.id
        ).action_assign()
        self.token_location_id.with_context(
            location_id=self.location_id.id,
            ignore_expected_location=True,
        ).action_call()
        return {
            "type": "ir.actions.act_multi",
            "actions": [
                {"type": "ir.actions.act_window_close"},
                {"type": "ir.actions.act_view_reload"},
            ],
        }
