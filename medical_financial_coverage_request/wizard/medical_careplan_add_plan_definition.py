# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalCareplanAddPlanDefinition(models.TransientModel):
    _inherit = 'medical.careplan.add.plan.definition'

    coverage_id = fields.Many2one(
        'medical.coverage',
        related='careplan_id.coverage_id'
    )
    center_id = fields.Many2one(
        'res.partner',
        related='careplan_id.center_id',
        readonly=True,
    )
    coverage_template_id = fields.Many2one(
        'medical.coverage.template',
        related='coverage_id.coverage_template_id'
    )
    agreement_ids = fields.Many2many(
        'medical.coverage.agreement',
        compute='_compute_agreements'
    )
    agreement_line_id = fields.Many2one(
        'medical.coverage.agreement.item',
        domain="[('coverage_agreement_id', 'in', agreement_ids),"
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
    authorization_method_id = fields.Many2one(
        'medical.authorization.method',
        related='agreement_line_id.authorization_method_id'
    )
    authorization_format_id = fields.Many2one(
        'medical.authorization.format',
        related='agreement_line_id.authorization_format_id'
    )
    authorization_required = fields.Boolean(
        related='agreement_line_id.authorization_method_id.'
                'authorization_required'
    )
    authorization_number = fields.Char()
    authorization_information = fields.Text(
        related='agreement_line_id.authorization_format_id.'
                'authorization_information',
        readonly=True,
    )

    @api.depends('coverage_template_id', 'center_id')
    def _compute_agreements(self):
        for rec in self:
            rec.agreement_ids = self.env['medical.coverage.agreement'].search([
                ('coverage_template_ids', '=', rec.coverage_template_id.id),
                ('center_ids', '=', rec.center_id.id)
            ])

    def _get_values(self):
        values = super(MedicalCareplanAddPlanDefinition, self)._get_values()
        values['coverage_id'] = self.careplan_id.coverage_id.id
        values['coverage_agreement_item_id'] = self.agreement_line_id.id
        values['authorization_method_id'] = self.authorization_method_id.id
        values['authorization_number'] = self.authorization_number
        values[
            'coverage_agreement_id'
        ] = self.agreement_line_id.coverage_agreement_id.id
        values['plan_definition_id'] = self.plan_definition_id.id
        values['center_id'] = self.center_id.id
        if (
            self.authorization_method_id.authorization_required and
            not self.authorization_format_id.check_value(
                self.authorization_number
            )
        ):
            raise ValidationError(_('Authorization number is not valid'))
        return values

    @api.multi
    def _run(self):
        res = super()._run()
        if res and not self.careplan_id.service_id:
            self.careplan_id.write({'service_id': self.product_id.id})
        return res
