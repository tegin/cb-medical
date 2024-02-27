# Copyright 2024 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalCareplanAddPlanDefinition(models.TransientModel):

    _inherit = "medical.careplan.add.plan.definition"

    send_to_queue = fields.Boolean(default=True)

    def _get_context(self):
        result = super()._get_context()
        result["do_not_generate_queue_task"] = not self.send_to_queue
        return result
