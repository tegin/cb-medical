# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDepartment(models.Model):

    _name = "medical.department"
    _inherit = "medical.abstract"
    _description = "Medical Department"

    name = fields.Char(required=True)
    diagnostic_report_header = fields.Html(translate=True, sanitize=False)
    report_category_ids = fields.One2many(
        comodel_name="medical.report.category",
        inverse_name="medical_department_id",
    )
    user_ids = fields.Many2many("res.users")
    without_practitioner = fields.Boolean(
        help="When marked, the practitioner "
        "will not appear in the report when validated"
    )

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.department") or "/"
        )
