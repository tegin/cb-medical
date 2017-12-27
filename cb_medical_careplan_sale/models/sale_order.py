# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrder(models.AbstractModel):
    _inherit = 'sale.order'

    careplan_id = fields.Many2one(
        'medical.careplan'
    )

    coverage_agreement_id = fields.Many2one(
        'medical.coverage.agreement'
    )
