# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PlanDefinitionAction(models.Model):
    _inherit = 'workflow.plan.definition.action'

    variable_fee = fields.Float(
        string='Variable fee (%)',
        default='0.0',
    )
    fixed_fee = fields.Float(
        string='Fixed fee',
        default='0.0',
    )
    medical_commission = fields.Boolean(
        related='activity_definition_id.service_id.medical_commission'
    )
