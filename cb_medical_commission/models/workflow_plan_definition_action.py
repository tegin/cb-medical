# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


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
    make_invisible = fields.Boolean(
        default=True,
        compute='_compute_hide_fee',
    )

    @api.depends('activity_definition_id')
    def _compute_hide_fee(self):
        for rec in self:
            if self.activity_definition_id.service_id.\
                    medical_commission:
                rec.make_invisible = False
            else:
                rec.make_invisible = True

    @api.multi
    def execute_action(self, vals, parent=False):
        vals.update({
            'variable_fee': self.variable_fee,
            'fixed_fee': self.fixed_fee,
        })
        super(PlanDefinitionAction, self).execute_action(vals, parent=False)
