# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_medical_values(
        self, vals, parent=False, plan=False, action=False
    ):
        res = super(ActivityDefinition, self)._get_medical_values(
            vals, parent, plan, action
        )
        if action:
            is_billable = action.is_billable
            is_breakdown = False
        elif plan:
            is_billable = plan.is_billable
            is_breakdown = plan.is_breakdown
        else:
            is_billable = False
            is_breakdown = False
        res["is_billable"] = is_billable
        res["is_breakdown"] = is_breakdown
        if parent and not res.get("center_id", False):
            res["center_id"] = parent.center_id.id
        elif res.get("careplan_id", False) and not res.get("center_id", False):
            res["center_id"] = (
                self.env["medical.careplan"]
                .browse(res["careplan_id"])
                .center_id.id
            )
        if not action or not self.env[self.model_id.model]._pass_performer(
            self, parent, plan, action
        ):
            res["performer_id"] = False
        if action:
            res["performer_id"] = action.performer_id.id or False
        return res
