# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    coverage_id = fields.Many2one(
        "medical.coverage",
        track_visibility=True,
        required=False,
        domain="[('patient_id', '=', patient_id)]",
    )
    coverage_agreement_item_id = fields.Many2one(
        "medical.coverage.agreement.item", readonly=True, ondelete="restrict"
    )
    coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement", readonly=True, ondelete="restrict"
    )
    authorization_method_id = fields.Many2one(
        comodel_name="medical.authorization.method",
        track_visibility=True,
        readonly=True,
        ondelete="restrict",
    )
    authorization_number = fields.Char(track_visibility=True)
    authorization_status = fields.Selection(
        [
            ("pending", "Pending authorization"),
            ("not-authorized", "Not authorized"),
            ("authorized", "Authorized"),
        ],
        readonly=True,
    )
    can_deactivate = fields.Boolean(compute="_compute_can_deactivate")
    parent_id = fields.Integer(index=True)
    parent_model = fields.Char(index=True)

    @api.depends("state")
    def _compute_can_deactivate(self):
        for record in self:
            record.can_deactivate = record.state == "draft"

    def update_plan_vals(self, relations):
        return {
            "patient_id": self.patient_id.id,
            "careplan_id": self.careplan_id.id or False,
            "center_id": self.center_id.id or False,
            "relations": relations,
            "encounter_id": self.encounter_id.id or False,
            "coverage_id": self.coverage_id.id,
            "coverage_agreement_item_id": self.coverage_agreement_item_id.id,
            "authorization_method_id": self.authorization_method_id.id,
            "authorization_number": self.authorization_number,
            "coverage_agreement_id": self.coverage_agreement_id.id,
        }

    def _update_plan_parent_vals(self, plan, coverage_agreement_item_id):
        cov = coverage_agreement_item_id.coverage_agreement_id.id
        return {
            "plan_definition_id": plan.id,
            "is_billable": plan.is_billable,
            "is_breakdown": plan.is_breakdown,
            "coverage_agreement_item_id": coverage_agreement_item_id.id,
            "coverage_agreement_id": cov,
            "service_id": coverage_agreement_item_id.product_id.id,
            "name": coverage_agreement_item_id.product_id.name,
        }

    def update_plan_definition(self, plan, coverage_agreement_item_id):
        return self.write(
            self._update_plan_parent_vals(plan, coverage_agreement_item_id)
        )

    def check_plan_definition_change(self, plan):
        relations = {}
        activities = {}
        for action in plan.action_ids:
            if not activities.get(action.activity_definition_id.id, False):
                activities[action.activity_definition_id.id] = []
            activities[action.activity_definition_id.id].append(action.id)
        for model in self._get_request_models():
            for child in (
                self.env[model]
                .search(
                    [
                        (self._get_parent_field_name(), "=", self.id),
                        ("active", "=", True),
                    ]
                )
                .sorted("can_deactivate")
            ):
                if child.activity_definition_id.id in activities:
                    action = activities[child.activity_definition_id.id].pop()
                    relations[action] = child.id
                    if len(activities[child.activity_definition_id.id]) == 0:
                        del activities[child.activity_definition_id.id]
                elif child.can_deactivate:
                    child.toggle_active()
                else:
                    raise ValidationError(_("Plans cannot be interchanged"))
        return relations

    def change_plan_definition(self, coverage_agreement_item_id):
        self.ensure_one()
        plan = coverage_agreement_item_id.plan_definition_id
        if not self.active:
            raise ValidationError(
                _("Element is inactive, your cannot change plan")
            )
        if self.plan_definition_id == plan:
            self.update_plan_definition(plan, coverage_agreement_item_id)
            return
        raise ValidationError(_("Plans are not equivalent"))

    def change_authorization(self, method, **kwargs):
        self.ensure_one()
        vals = self.coverage_agreement_item_id._check_authorization(
            method, **kwargs
        )
        vals.update(self._change_authorization_vals(method, vals, **kwargs))
        self._change_authorization(vals, **kwargs)

    def _change_authorization_vals(self, method, vals, **kwargs):
        # This hook allows to process the data using the original request
        return {}

    def _change_authorization(self, vals, **kwargs):
        self.filtered(lambda r: r.is_billable).write(vals)
        fieldname = self._get_parent_field_name()
        for request in self:
            for model in self._get_request_models():
                self.env[model].search(
                    [
                        (fieldname, "=", request.id),
                        ("parent_id", "=", request.id),
                        ("parent_model", "=", request._name),
                        ("state", "!=", "cancelled"),
                    ]
                )._change_authorization(vals, **kwargs)

    def _update_related_activity_vals(self, vals, parent, plan, action):
        res = {}
        res["coverage_agreement_item_id"] = False
        res["coverage_agreement_id"] = False
        res["authorization_method_id"] = False
        if parent:
            res["parent_model"] = parent._name
            res["parent_id"] = parent.id
        if res.get("is_billable", False) and vals.get("coverage_id", False):
            coverage_template = (
                self.env["medical.coverage"]
                .browse(vals.get("coverage_id"))
                .coverage_template_id
            )
            cai = self.env["medical.coverage.agreement.item"].get_item(
                self.service_id,
                coverage_template,
                parent.center_id or vals.get("center_id"),
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
            vals = cai._check_authorization(cai.authorization_method_id, **res)
            res.update(vals)
        return res

    def _update_related_activity(self, vals, parent, plan, action):
        self.write(
            self._update_related_activity_vals(vals, parent, plan, action)
        )
