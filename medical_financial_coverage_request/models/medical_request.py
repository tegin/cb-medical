# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    coverage_id = fields.Many2one(
        "medical.coverage",
        tracking=True,
        required=False,
        domain="[('patient_id', '=', patient_id)]",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    coverage_agreement_item_id = fields.Many2one(
        "medical.coverage.agreement.item", readonly=True, ondelete="restrict"
    )
    coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement", readonly=True, ondelete="restrict"
    )
    authorization_method_id = fields.Many2one(
        comodel_name="medical.authorization.method",
        tracking=True,
        readonly=True,
        ondelete="restrict",
        states={"draft": [("readonly", False)]},
    )
    authorization_number = fields.Char(
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    authorization_number_extra_1 = fields.Char(tracking=True)
    authorization_status = fields.Selection(
        [
            ("pending", "Pending authorization"),
            ("not-authorized", "Not authorized"),
            ("authorized", "Authorized"),
        ],
        readonly=True,
    )
    parent_id = fields.Integer(index=True)
    parent_model = fields.Char(index=True)
    is_billable = fields.Boolean(string="Is billable?", default=False, tracking=True)
    is_breakdown = fields.Boolean(default=False, tracking=True)
    third_party_bill = fields.Boolean(default=False, tracking=True)
    center_id = fields.Many2one(
        "res.partner",
        domain=[("is_center", "=", True)],
        required=True,
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    active = fields.Boolean(default=True)

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

    def change_plan_definition(self, coverage_agreement_item_id):
        self.ensure_one()
        plan = coverage_agreement_item_id.plan_definition_id
        if not self.active:
            raise ValidationError(_("Element is inactive, your cannot change plan"))
        if self.plan_definition_id == plan:
            self.update_plan_definition(plan, coverage_agreement_item_id)
            return
        raise ValidationError(_("Plans are not equivalent"))

    def change_authorization(self, method, **kwargs):
        self.ensure_one()
        vals = self.coverage_agreement_item_id._check_authorization(method, **kwargs)
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

    @api.model
    def _pass_performer(self, activity, parent, plan, action):
        return False
