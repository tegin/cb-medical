# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCoverageAgreement(models.Model):
    _inherit = 'medical.coverage.agreement'

    invoice_group_method_id = fields.Many2one(
        string='Invoice Group Method',
        comodel_name='sale.invoice.group.method',
        track_visibility=True,
    )
