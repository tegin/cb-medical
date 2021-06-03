# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_medical_values(
        self, vals, parent=False, plan=False, action=False
    ):
        res = super(ActivityDefinition, self)._get_medical_values(
            vals, parent, plan, action
        )
        res["is_billable"] = False if action else plan.is_billable
        res["is_breakdown"] = plan.is_breakdown if not action else False
        if parent and not res.get("center_id", False):
            res["center_id"] = parent.center_id.id
        elif res.get("careplan_id", False) and not res.get("center_id", False):
            res["center_id"] = (
                self.env["medical.careplan"]
                .browse(res["careplan_id"])
                .center_id.id
            )
        if not self.env[self.model_id.model]._pass_performer(
            self, parent, plan, action
        ):
            res["performer_id"] = False
        if action.performer_id:
            res["performer_id"] = action.performer_id.id
        return res
