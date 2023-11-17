# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WorkflowPlanDefinition(models.Model):
    _inherit = "workflow.plan.definition"

    generate_queue_task = fields.Selection(
        [("performer", "Performer"), ("area", "Area")]
    )
    queue_area_id = fields.Many2one("queue.area")

    @api.constrains("generate_queue_task", "performer_required")
    def _check_generate_token(self):
        for record in self:
            if (
                record.generate_queue_task == "performer"
                and not record.performer_required
            ):
                raise ValidationError(
                    _(
                        "Performer must be required in order to generate task by performer"
                    )
                )
