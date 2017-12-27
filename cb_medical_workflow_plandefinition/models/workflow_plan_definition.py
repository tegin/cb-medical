# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PlanDefinition(models.Model):
    _inherit = 'workflow.plan.definition'

    is_billable = fields.Boolean(
        string='Is billable?',
        default=True,
    )
    is_breakdown = fields.Boolean(
        string='Possible breakdown?',
        default=True,
    )

    def get_request_group_vals(self, vals):
        agreement_item_id = self.env['medical.coverage.agreement.item'].browse(
            vals.get('coverage_agreement_item_id')
        )
        values = vals.copy()
        values['service_id'] = agreement_item_id.product_id.id
        values['is_billable'] = self.is_billable
        values['is_breakdown'] = self.is_breakdown
        return values

    @api.multi
    def execute_plan_definition(self, vals, parent=False):
        self.ensure_one()
        request_group = parent
        if (
            not request_group and
            not self.activity_definition_id and
            vals.get('coverage_agreement_item_id', False)
        ):
            request_group = self.env['medical.request.group'].create(
                self.get_request_group_vals(vals)
            )
        return super(PlanDefinition, self).execute_plan_definition(
            vals, request_group)
