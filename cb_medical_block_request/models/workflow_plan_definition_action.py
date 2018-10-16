# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PlanDefinitionAction(models.Model):
    _inherit = 'workflow.plan.definition.action'

    is_blocking = fields.Boolean(
        string='Is Blocking?',
        default=False,
    )
