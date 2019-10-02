# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PlanDefinitionAction(models.Model):
    _inherit = "workflow.plan.definition.action"

    trigger_action_ids = fields.Many2many(
        "workflow.plan.definition.action",
        "trigger_actions",
        "triggered_action_id",
        "trigger_action_id",
        "Actions that will be triggered",
        domain="[('plan_definition_id', '=', parent.id), "
        "('id', '!=', active_id), "
        "('execute_plan_definition_id', '=', False)]",
    )
    triggerer_action_ids = fields.Many2many(
        "workflow.plan.definition.action",
        "trigger_actions",
        "trigger_action_id",
        "triggered_action_id",
        "Actions that will trigger this action",
        readonly=True,
    )

    def _check_trigger_recursion(self, ids):
        if not self:
            return False
        if any(el in self.ids for el in ids):
            return True
        return self.mapped("trigger_action_ids")._check_trigger_recursion(
            ids + self.ids
        )

    @api.constrains("trigger_action_ids")
    def _check_trigger_actions(self):
        for rec in self:
            if rec.trigger_action_ids._check_trigger_recursion([rec.id]):
                raise ValidationError(_("Trigger entered on a loop"))
