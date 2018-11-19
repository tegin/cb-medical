# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class MedicalCoverageAgreementItem(models.Model):
    _name = 'medical.coverage.agreement.item'
    _description = "Medical Coverage Agreement Item"
    _rec_name = 'product_id'

    def _default_coverage_percentage(self):
        agreement_id = self.env.context.get('default_coverage_agreement_id',
                                            False)
        agreement = self.env['medical.coverage.agreement'].browse(agreement_id)
        if agreement:
            if agreement.principal_concept == 'coverage':
                return 100.0
            else:
                return 0.0

    plan_definition_id = fields.Many2one(
        string='Plan definition',
        comodel_name='workflow.plan.definition',
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        related='product_id.product_tmpl_id',
        readonly=True,
        store=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Service',
        ondelete='restrict',
        domain=[('type', '=', 'service'), ('sale_ok', '=', True)],
        required=True,
    )
    categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Category',
        ondelete='restrict',
        related='product_id.categ_id',
        store=True,
        readonly=True,
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
    template_id = fields.Many2one(
        'medical.coverage.agreement', readonly=True,
        related='coverage_agreement_id.template_id',
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

    @api.onchange('product_id')
    def _onchange_product(self):
        related = self.template_id.item_ids.filtered(
            lambda r: r.product_id == self.product_id
        )
        if related:
            self._update_by_related(related)

    def _update_by_related(self, related):
        rounding = self.currency_id.rounding
        if not self.plan_definition_id:
            self.plan_definition_id = related.plan_definition_id
        if not float_compare(
            self.total_price, 0, precision_rounding=rounding
        ):
            self.total_price = related.total_price

    @api.multi
    def _compute_price(self):
        for rec in self:
            rec.coverage_price = \
                (rec.coverage_percentage * rec.total_price) / 100
            rec.private_price = \
                ((100 - rec.coverage_percentage) * rec.total_price) / 100

    @api.constrains('product_id', 'coverage_agreement_id', 'active')
    def _check_product(self):
        for rec in self.filtered(lambda r: r.active):
            if self.search([
                ('id', '!=', rec.id),
                ('coverage_agreement_id', '=', rec.coverage_agreement_id.id),
                ('product_id', '=', rec.product_id.id),
                ('active', '=', True),
            ], limit=1):
                raise ValidationError(_(
                    'Product must be unique for an agreement'
                ))

    def _copy_agreement_vals(self, agreement):
        return {
            'coverage_agreement_id': agreement.id,
            'plan_definition_id': self.plan_definition_id.id or False,
            'product_id': self.product_id.id,
            'total_price': self.total_price,
        }
