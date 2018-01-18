# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalCoverageTemplate(models.Model):
    _inherit = 'medical.coverage.template'

    agreement_ids = fields.Many2many(
        string='Coverage Templates',
        comodel_name='medical.coverage.agreement',
        relation='medical_coverage_agreement_medical_coverage_template_rel',
        column1='coverage_template_id',
        column2='agreement_id',
        help='Coverage templates related to this agreement',
    )
    unique_product = fields.Boolean(
        compute='_compute_unique_product',
        store=True,
    )

    @api.depends('agreement_ids', 'agreement_ids.item_ids')
    def _compute_unique_product(self):
        for rec in self:
            all_products = []
            for agreement in rec.agreement_ids:
                for item in agreement.item_ids:
                    all_products += item.product_id
            if len(all_products) != len(set(all_products)):
                rec.unique_product = False
            else:
                rec.unique_product = True

    @api.constrains('unique_product')
    def _check_unique_product(self):
        for rec in self:
            if not rec.unique_product:
                raise ValidationError(_(
                    "One of this actions cannot be completed:\n- If you are "
                    "trying to add an agreement to a coverage template then "
                    "this agreement can't be added as it contains one or more "
                    "products that already exist in another agreement "
                    "belonging to this Coverage Template.\n"
                    "- If you are trying to add a new product to an Agreement "
                    "that means there is a coverage template that "
                    "already has this product in another Agreement."))
