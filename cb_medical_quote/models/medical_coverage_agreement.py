# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalCoverageAgreement(models.Model):

    _inherit = "medical.coverage.agreement"

    quote_ids = fields.One2many(
        "medical.quote", inverse_name="origin_agreement_id"
    )
