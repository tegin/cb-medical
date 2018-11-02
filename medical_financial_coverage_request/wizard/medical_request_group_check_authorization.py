# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalRequestGroupCheckAuthorization(models.TransientModel):
    _name = 'medical.request.group.check.authorization'

    request_group_id = fields.Many2one(
        'medical.request.group',
        requierd=True,
        readonly=True,
    )
    coverage_agreement_item_id = fields.Many2one(
        'medical.coverage.agreement.item',
        related='request_group_id.coverage_agreement_item_id',
    )
    product_id = fields.Many2one(
        'product.product',
        readonly=True,
        related="coverage_agreement_item_id.product_id"
    )
    plan_definition_id = fields.Many2one(
        comodel_name='workflow.plan.definition',
        readonly=True,
        related='coverage_agreement_item_id.plan_definition_id'
    )
    authorization_method_id = fields.Many2one(
        'medical.authorization.method',
        readonly=True,
        related='coverage_agreement_item_id.authorization_method_id'
    )
    authorization_format_id = fields.Many2one(
        'medical.authorization.format',
        readonly=True,
        related='coverage_agreement_item_id.authorization_format_id'
    )
    authorization_required = fields.Boolean(
        readonly=True,
        related='coverage_agreement_item_id.authorization_method_id.'
                'authorization_required'
    )
    authorization_number = fields.Char()
    authorization_information = fields.Text(
        related='coverage_agreement_item_id.authorization_format_id.'
                'authorization_information',
        readonly=True,
    )

    def _get_kwargs(self):
        return {
            'authorization_number': self.authorization_number,
        }

    @api.multi
    def run(self):
        self.ensure_one()
        self.request_group_id.change_authorization(**self._get_kwargs())
        return {}
