# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalReportCategory(models.Model):

    _name = "medical.report.category"
    _inherit = "medical.abstract"
    _description = "Medical Report Category"
    _order = "sequence"

    name = fields.Char(required=True)
    medical_department_id = fields.Many2one("medical.department")

    sequence = fields.Integer(default=20)

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.report.category")
            or "/"
        )
