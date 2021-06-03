# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    request_group_ids = fields.One2many(
        "medical.request.group", inverse_name="patient_id"
    )
    last_coverage_id = fields.Many2one(
        "medical.coverage", compute="_compute_last_coverage"
    )

    @api.depends("request_group_ids")
    def _compute_last_coverage(self):
        for rec in self:
            requests = rec.request_group_ids.filtered(
                lambda r: r.coverage_id
            ).sorted("id", reverse=True)
            if requests:
                rec.last_coverage_id = requests[0].coverage_id
            else:
                rec.last_coverage_id = False
