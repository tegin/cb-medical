# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalRequestGroupChangePlan(models.TransientModel):
    _name = "medical.request.group.change.plan"

    request_group_id = fields.Many2one(
        "medical.request.group", requierd=True, readonly=True
    )
    careplan_id = fields.Many2one(
        "medical.careplan",
        related="request_group_id.careplan_id",
        readonly=True,
    )
    patient_id = fields.Many2one(
        "medical.patient", related="request_group_id.patient_id", readonly=True
    )
    coverage_id = fields.Many2one(
        "medical.coverage", readonly=True, related="careplan_id.coverage_id"
    )
    center_id = fields.Many2one(
        "res.partner", related="careplan_id.center_id", readonly=True
    )
    coverage_template_id = fields.Many2one(
        "medical.coverage.template",
        readonly=True,
        related="coverage_id.coverage_template_id",
    )
    agreement_ids = fields.Many2many(
        "medical.coverage.agreement", compute="_compute_agreements"
    )
    agreement_line_id = fields.Many2one(
        "medical.coverage.agreement.item",
        domain="[('coverage_agreement_id', 'in', agreement_ids),"
        "('plan_definition_id', '!=', False)]",
    )
    product_id = fields.Many2one(
        "product.product",
        readonly=True,
        related="agreement_line_id.product_id",
    )
    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        readonly=True,
        related="agreement_line_id.plan_definition_id",
    )
    authorization_method_id = fields.Many2one(
        "medical.authorization.method",
        readonly=True,
        related="agreement_line_id.authorization_method_id",
    )
    authorization_format_id = fields.Many2one(
        "medical.authorization.format",
        readonly=True,
        related="agreement_line_id.authorization_format_id",
    )
    authorization_required = fields.Boolean(
        readonly=True,
        related="agreement_line_id.authorization_method_id."
        "authorization_required",
    )
    authorization_number = fields.Char()
    authorization_information = fields.Text(
        related="agreement_line_id.authorization_format_id."
        "authorization_information",
        readonly=True,
    )

    @api.depends("coverage_template_id", "center_id")
    def _compute_agreements(self):
        for rec in self:
            rec.agreement_ids = self.env["medical.coverage.agreement"].search(
                [
                    (
                        "coverage_template_ids",
                        "=",
                        rec.coverage_template_id.id,
                    ),
                    ("center_ids", "=", rec.center_id.id),
                ]
            )

    @api.multi
    def run(self):
        self.ensure_one()
        self.request_group_id.change_plan_definition(self.agreement_line_id)
        return {}
