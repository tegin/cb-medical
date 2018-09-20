from odoo import models


class PlanDefinition(models.Model):
    _inherit = 'workflow.plan.definition'

    def get_request_group_vals(self, vals):
        res = super().get_request_group_vals(vals)
        res['parent_model'] = self.env.context.get('origin_model', False)
        res['parent_id'] = self.env.context.get('origin_id', False)
        return res
