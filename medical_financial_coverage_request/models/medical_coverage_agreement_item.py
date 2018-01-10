# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCoverageAgreementItem(models.Model):
    _inherit = 'medical.coverage.agreement.item'

    coverage_template_ids = fields.Many2many(
        string='Coverage Templates',
        comodel_name='medical.coverage.template',
        related="coverage_agreement_id.coverage_template_ids"
    )
