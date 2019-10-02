from odoo import models


class WorkflowActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_medical_values(
        self, vals, parent=False, plan=False, action=False
    ):
        res = super()._get_medical_values(vals, parent, plan, action)
        if action and action.laboratory_service_ids:
            res["laboratory_service_ids"] = [
                (6, 0, action.laboratory_service_ids.ids)
            ]
        return res
