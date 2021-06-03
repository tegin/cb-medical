# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PlanDefinition(models.Model):
    _inherit = "workflow.plan.definition"

    is_billable = fields.Boolean(
        string="Is billable?", default=True, track_visibility=True
    )
    third_party_bill = fields.Boolean(
        string="Will be payed to the third party?", default=False
    )
    is_breakdown = fields.Boolean(
        string="Possible breakdown?", default=True, track_visibility=True
    )
    performer_required = fields.Boolean(default=False)

    @api.multi
    @api.constrains("is_billable", "third_party_bill", "direct_action_ids")
    def _check_third_party_bill(self):
        for plan in self:
            if plan.third_party_bill:
                if plan.is_breakdown:
                    raise ValidationError(
                        _("Third party plans cannot be broken")
                    )
                if not plan.is_billable:
                    raise ValidationError(
                        _("Third party plans must be billable")
                    )
                if len(plan.direct_action_ids.ids) > 1:
                    raise ValidationError(
                        _("Only one action is allowed for third party plans")
                    )
                if (
                    plan.direct_action_ids
                    and plan.direct_action_ids.is_billable
                ):
                    raise ValidationError(
                        _("Action cannot be billable on third party plans")
                    )

    def get_request_group_vals(self, vals):
        agreement_item_id = self.env["medical.coverage.agreement.item"].browse(
            vals.get("coverage_agreement_item_id")
        )
        values = vals.copy()
        values["service_id"] = agreement_item_id.product_id.id
        values["is_billable"] = self.is_billable
        values["is_breakdown"] = self.is_breakdown
        values["third_party_bill"] = self.third_party_bill
        return values

    @api.multi
    def execute_plan_definition(self, vals, parent=False):
        self.ensure_one()
        request_group = parent
        if (
            not request_group
            and not self.activity_definition_id
            and vals.get("coverage_agreement_item_id", False)
        ):
            request_group = self.env["medical.request.group"].create(
                self.get_request_group_vals(vals)
            )
        res = super().execute_plan_definition(vals, request_group)
        return request_group or res
