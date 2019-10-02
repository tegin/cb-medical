from odoo import models


class WorkflowActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_medical_values(
        self, vals, parent=False, plan=False, action=False
    ):
        res = super()._get_medical_values(vals, parent, plan, action)
        if action and action.location_type_id:
            res["location_type_id"] = action.location_type_id.id
        return res
