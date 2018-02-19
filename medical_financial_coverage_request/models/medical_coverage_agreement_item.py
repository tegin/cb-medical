# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCoverageAgreementItem(models.Model):
    _inherit = 'medical.coverage.agreement.item'

    def _default_authorization_method(self):
        agreement_id = self.env.context.get('default_coverage_agreement_id',
                                            False)
        agreement = self.env['medical.coverage.agreement'].browse(agreement_id)
        if agreement:
            return agreement.authorization_method_id

    def _default_authorization_format(self):
        agreement_id = self.env.context.get('default_coverage_agreement_id',
                                            False)
        agreement = self.env['medical.coverage.agreement'].browse(agreement_id)
        if agreement:
            return agreement.authorization_format_id

    coverage_template_ids = fields.Many2many(
        string='Coverage Templates',
        comodel_name='medical.coverage.template',
        related="coverage_agreement_id.coverage_template_ids"
    )
    authorization_method_id = fields.Many2one(
        'medical.authorization.method',
        default=_default_authorization_method,
        required=True
    )
    authorization_format_id = fields.Many2one(
        'medical.authorization.format',
        default=_default_authorization_format,
        required=True
    )
