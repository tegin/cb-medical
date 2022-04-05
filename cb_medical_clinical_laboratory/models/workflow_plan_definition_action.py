from odoo import api, fields, models


class WorkflowPlanDefinitinoAction(models.Model):
    _inherit = "workflow.plan.definition.action"

    laboratory_service_ids = fields.Many2many(
        "product.product", domain=[("laboratory_request_ok", "=", True)]
    )

    @api.onchange("activity_definition_id")
    def _onchange_activity_definition(self):
        laboratory = self.env.ref(
            "medical_clinical_laboratory.model_medical_laboratory_request"
        )
        for rec in self.filtered(lambda r: r.activity_definition_id):
            if rec.activity_definition_id.model_id != laboratory:
                rec.laboratory_service_ids = False
