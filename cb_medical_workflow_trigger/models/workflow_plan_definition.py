# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class PlanDefinition(models.Model):
    _inherit = "workflow.plan.definition"

    def _execute_plan_definition(self, vals, parent=False):
        res, result = super()._execute_plan_definition(vals, parent=parent)
        trigger_obj = self.env["medical.request.trigger"]
        for action in self.action_ids.filtered(lambda r: r.trigger_action_ids):
            model = action.activity_definition_id.model_id.model
            element = (
                self.env[model]
                .browse(result[model])
                .filtered(lambda r: r.plan_definition_action_id == action)
            )
            element.ensure_one()
            for trigger in action.trigger_action_ids:
                trigger_model = trigger.activity_definition_id.model_id.model
                trigger_element = (
                    self.env[trigger_model]
                    .browse(result[trigger_model])
                    .filtered(lambda r: r.plan_definition_action_id == trigger)
                )
                trigger_element.ensure_one()
                trigger_obj.create(
                    {
                        "request_id": element.id,
                        "request_model": element._name,
                        "trigger_id": trigger_element.id,
                        "trigger_model": trigger_element._name,
                    }
                )
        return res, result
