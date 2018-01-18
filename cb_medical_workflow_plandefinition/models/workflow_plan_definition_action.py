# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PlanDefinitionAction(models.Model):
    _inherit = 'workflow.plan.definition.action'

    is_billable = fields.Boolean(
        string='Is billable?',
        default=True,
    )
    activity_definition_id = fields.Many2one(
        string='Activity definition',
        comodel_name='workflow.activity.definition',
        domain="[('model_id', 'in', "
               "['medical.procedure.request', 'medical.medication.request'])]",
    )   # FHIR field: definition (Activity Definition)
