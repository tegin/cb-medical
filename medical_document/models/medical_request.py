# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    document_reference_ids = fields.One2many(
        string="Associated Documents",
        comodel_name="medical.document.reference",
        compute="_compute_document_reference_ids",
    )
    document_reference_count = fields.Integer(
        compute="_compute_document_reference_ids",
        string="# of Document References",
        copy=False,
        default=0,
    )
    document_reference_id = fields.Many2one(
        "medical.document.reference", required=False, readonly=True, index=True
    )  # the field must be created, but it should allways be null

    @api.constrains("document_reference_id")
    def check_document_reference(self):
        if self.filtered(lambda r: r.document_reference_id):
            raise ValidationError(
                _("Document reference cannot be parent of other documents.")
            )

    @api.model
    def _get_request_models(self):
        res = super(MedicalRequest, self)._get_request_models()
        res.append("medical.document.reference")
        return res

    @api.multi
    def _compute_document_reference_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            documents = self.env["medical.document.reference"].search(
                [(inverse_field_name, "=", rec.id)]
            )
            rec.document_reference_ids = [(6, 0, documents.ids)]
            rec.document_reference_count = len(rec.document_reference_ids)

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.document_reference_id)
        return res
