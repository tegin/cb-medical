# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_activity_values(
        self, vals, parent=False, plan=False, action=False
    ):
        res = super()._get_activity_values(vals, parent, plan, action)
        if "relations" in res.keys() and self.type_id == self.env.ref(
            "medical_workflow.medical_workflow"
        ):
            del res["relations"]
        return res

    def _get_medical_values(
        self, vals, parent=False, plan=False, action=False
    ):
        res = super()._get_medical_values(vals, parent, plan, action)

        res["coverage_agreement_item_id"] = False
        res["coverage_agreement_id"] = False
        res["authorization_method_id"] = False
        res["is_billable"] = False
        if parent:
            res["parent_model"] = parent._name
            res["parent_id"] = parent.id
        return res

    def _get_request_group_values(
        self, vals, parent=False, plan=False, action=False
    ):
        res = self._get_activity_values(vals, parent, plan, action)
        res["is_billable"] = True
        if vals.get("coverage_id", False):
            coverage_template = (
                self.env["medical.coverage"]
                .browse(vals.get("coverage_id"))
                .coverage_template_id
            )
            cai = self.env["medical.coverage.agreement.item"].get_item(
                self.service_id, coverage_template, vals["center_id"]
            )
            if not cai:
                raise ValidationError(
                    _(
                        "An element should exist on an agreement if it is billable"
                    )
                )
            res["coverage_agreement_item_id"] = cai.id
            res["coverage_agreement_id"] = cai.coverage_agreement_id.id
            res["authorization_method_id"] = cai.authorization_method_id.id
            new_vals = cai._check_authorization(
                cai.authorization_method_id, **res
            )
            res.update(new_vals)
        return res

    @api.multi
    def execute_activity(self, vals, parent=False, plan=False, action=False):
        self.ensure_one()
        if action.id in vals.get("relations", {}):
            activity = self.env[self.model_id.model].browse(
                vals["relations"][action.id]
            )
            activity._update_related_activity(vals, parent, plan, action)
            return activity
        if parent and action.is_billable:
            group_obj = self.env["medical.request.group"]
            request_vals = self._get_request_group_values(
                vals,
                self.env[parent.parent_model].browse(parent.parent_id),
                plan,
                action,
            )
            for key in request_vals.copy():
                if key not in group_obj._fields:
                    del request_vals[key]
            request_group = group_obj.create(request_vals)
            result = super().execute_activity(
                vals, request_group, plan, action
            )
            request_group.write(
                {"child_model": result._name, "child_id": result.id}
            )
            return result
        return super().execute_activity(vals, parent, plan, action)
