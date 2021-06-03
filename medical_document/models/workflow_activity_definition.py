# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    requires_document_template = fields.Boolean(
        compute="_compute_requires_document_template"
    )
    document_type_id = fields.Many2one(
        "medical.document.type",
        domain=[("state", "=", "current")],
        ondelete="restrict",
    )

    @api.depends("model_id")
    def _compute_requires_document_template(self):
        for record in self:
            record.requires_document_template = bool(
                record.model_id.model == "medical.document.reference"
            )

    @api.onchange("model_id")
    def _onchange_model(self):
        if self.model_id.model != "medical.document.reference":
            self.document_type_id = False

    def _get_medical_values(
        self, vals, parent=False, plan=False, action=False
    ):
        values = super(ActivityDefinition, self)._get_medical_values(
            vals, parent, plan, action
        )
        if self.model_id.model == "medical.document.reference":
            values["document_type_id"] = self.document_type_id.id
        return values
