# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PlanDefinitionAction(models.Model):
    _inherit = "workflow.plan.definition.action"

    is_billable = fields.Boolean(string="Is billable?", default=False)
    service_id = fields.Many2one(
        "product.product",
        related="activity_definition_id.service_id",
        readonly=True,
    )
    performer_id = fields.Many2one(
        "res.partner", domain=[("is_practitioner", "=", True)]
    )
