# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCoverageAgreement(models.Model):
    _inherit = "medical.coverage.agreement"

    authorization_method_id = fields.Many2one(
        "medical.authorization.method", required=True
    )
    authorization_format_id = fields.Many2one(
        "medical.authorization.format", required=True
    )
