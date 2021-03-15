# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_department = fields.Boolean(default=False, string="Is Medical Department")
    department_identifier = fields.Char(readonly=True)
    diagnostic_report_header = fields.Html(string="Diagnostic Report Header", translate=True)

    @api.model
    def _get_medical_identifiers(self):
        res = super(ResPartner, self)._get_medical_identifiers()
        res.append(
            (
                "is_medical",
                "is_department",
                "department_identifier",
                self._get_department_identifier,
            )
        )
        return res

    @api.model
    def _get_department_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.department") or "/"
        )
