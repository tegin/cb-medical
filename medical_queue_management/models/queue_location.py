# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class QueueLocation(models.Model):

    _inherit = "queue.location"

    action_ids = fields.Many2many("queue.location.action")
    allows_flag = fields.Boolean()

    def name_get(self):
        previous_result = super().name_get()
        if not self.env.context.get("custom_search"):
            return previous_result
        res = []
        for record, (record_id, base_name) in zip(self, previous_result):
            if record.state == "working":
                display_name = f"{base_name} ({_('Busy')} 🔴)"
            else:
                display_name = f"{base_name} 🟢"
            res.append((record_id, display_name))
        return res
