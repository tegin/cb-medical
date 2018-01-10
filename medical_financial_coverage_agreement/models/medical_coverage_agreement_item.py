# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class MedicalCoverageAgreementItem(models.Model):
    _name = 'medical.coverage.agreement.item'
    _description = "Medical Coverage Agreement Item"
    _rec_name = 'product_id'

    def _default_coverage_percentage(self):
        agreement_id = self.env.context.get('default_coverage_agreement_id',
                                            False)
        agreement = self.env['medical.coverage.agreement'].browse(agreement_id)
        if agreement:
            if agreement.payor == 'coverage':
                return 100.0
            else:
                return 0.0

    plan_definition_id = fields.Many2one(
        string='Plan definition',
        comodel_name='workflow.plan.definition',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        ondelete='cascade',
        required=True,
    )
    total_price = fields.Float(
        string='Total price',
        required=True,
    )
    coverage_percentage = fields.Float(
        string='Coverage %',
        required=True,
        default=_default_coverage_percentage,
    )
    coverage_agreement_id = fields.Many2one(
        comodel_name='medical.coverage.agreement',
        string='Medical agreement',
        index=True,
        ondelete='cascade',
    )
    currency_id = fields.Many2one(
        related='coverage_agreement_id.currency_id',
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        readonly=True,
        related='coverage_agreement_id.company_id',
        store=True,
    )
    coverage_price = fields.Float(
        string='Coverage price',
        compute='_compute_price',
    )
    private_price = fields.Float(
        string='Private price',
        compute='_compute_price',
    )
    active = fields.Boolean(
        default=True
    )

    @api.multi
    def _compute_price(self):
        for rec in self:
            rec.coverage_price = \
                (rec.coverage_percentage * rec.total_price) / 100
            rec.private_price = \
                ((100 - rec.coverage_percentage) * rec.total_price) / 100

    _sql_constraints = [
        ('product_id_agreement_id_unique',
         'unique(product_id, coverage_agreement_id)',
         _('Product has to be unique in each agreement!'))]
