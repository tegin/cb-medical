# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCareplanAddPlanDefinition(models.TransientModel):
    _inherit = 'medical.careplan.add.plan.definition'

    coverage_id = fields.Many2one(
        'medical.coverage',
        related='careplan_id.coverage_id'
    )
    coverage_template_id = fields.Many2one(
        'medical.coverage.template',
        related='coverage_id.coverage_template_id'
    )
    agreement_line_id = fields.Many2one(
        'medical.coverage.agreement.item',
        domain="[('coverage_template_ids', '=', coverage_template_id),"
               "('plan_definition_id', '!=', False)]"
    )
    product_id = fields.Many2one(
        'product.product',
        related="agreement_line_id.product_id"
    )
    plan_definition_id = fields.Many2one(
        comodel_name='workflow.plan.definition',
        related='agreement_line_id.plan_definition_id'
    )

    def _get_values(self):
        values = super(MedicalCareplanAddPlanDefinition, self)._get_values()
        values['coverage_id'] = self.careplan_id.coverage_id.id
        values['coverage_agreement_item_id'] = self.agreement_line_id.id
        values[
            'coverage_agreement_id'
        ] = self.agreement_line_id.coverage_agreement_id.id
        return values
