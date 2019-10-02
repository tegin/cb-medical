from odoo import fields, models


class WorkflowPlanDefinitionAction(models.Model):
    _inherit = "workflow.plan.definition.action"

    location_type_id = fields.Many2one("medical.location.type")
    model_id = fields.Many2one(
        "ir.model", related="activity_definition_id.model_id", readonly=True
    )
