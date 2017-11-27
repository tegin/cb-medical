# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PlanDefinition(models.Model):
    _inherit = 'workflow.plan.definition'

    is_billable = fields.Boolean(
        string='Is billable?',
        default=True,
    )
    is_breakdown = fields.Boolean(
        string='Possible breakdown?',
        default=True,
    )
