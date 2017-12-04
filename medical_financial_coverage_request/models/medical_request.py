# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    coverage_id = fields.Many2one(
        'medical.coverage',
        required=False,
        domain="[('patient_id', '=', patient_id)]"
    )
    coverage_agreement_item_id = fields.Many2one(
        'medical.coverage.agreement.item',
        readonly=True,
        ondelete='restrict'
    )
    coverage_agreement_id = fields.Many2one(
        'medical.coverage.agreement',
        readonly=True,
        ondelete='restrict'
    )
