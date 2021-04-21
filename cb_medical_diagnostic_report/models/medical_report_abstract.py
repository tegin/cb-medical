# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalReportAbstract(models.AbstractModel):

    _inherit = "medical.report.abstract"

    report_category_id = fields.Many2one("medical.report.category")
    medical_department_id = fields.Many2one(
        "medical.department",
        related="report_category_id.medical_department_id",
        store=True,
    )
    medical_department_header = fields.Html()
