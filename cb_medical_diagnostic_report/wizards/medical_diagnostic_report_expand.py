# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDiagnosticReportExpand(models.TransientModel):

    _inherit = "medical.diagnostic.report.expand"
    report_category_id = fields.Many2one(
        "medical.report.category",
        related="diagnostic_report_id.report_category_id",
    )
