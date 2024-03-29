# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCoverageAgreement(models.Model):
    _inherit = "medical.coverage.agreement"

    invoice_group_method_id = fields.Many2one(
        string="Invoice Group Method",
        comodel_name="invoice.group.method",
        tracking=True,
    )
    file_reference = fields.Char()
    discount = fields.Float(
        default=0.0, help="General discount applied on the final invoices"
    )

    def _check_authorization(self, method, **kwargs):
        res = super()._check_authorization(method, **kwargs)
        res["invoice_group_method_id"] = method.invoice_group_method_id.id or False
        return res
