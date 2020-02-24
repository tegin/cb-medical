# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    laboratory_request_ids = fields.One2many(
        string="Laboratory requests",
        comodel_name="medical.laboratory.request",
        compute="_compute_laboratory_request_ids",
    )
    laboratory_request_count = fields.Integer(
        compute="_compute_laboratory_request_ids",
        string="# of Laboratory requests",
        copy=False,
        default=0,
    )
    laboratory_request_id = fields.Many2one(
        "medical.laboratory.request", required=False, readonly=True
    )

    @api.model
    def _get_request_models(self):
        res = super(MedicalRequest, self)._get_request_models()
        res.append("medical.laboratory.request")
        return res

    @api.multi
    def _compute_laboratory_request_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            requests = self.env["medical.laboratory.request"].search(
                [(inverse_field_name, "=", rec.id)]
            )
            rec.laboratory_request_ids = [(6, 0, requests.ids)]
            rec.laboratory_request_count = len(rec.laboratory_request_ids)

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.laboratory_request_id)
        return res
