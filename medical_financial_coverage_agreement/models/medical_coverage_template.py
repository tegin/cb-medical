# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


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
