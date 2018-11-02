# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class MedicalRequestGroup(models.Model):
    _inherit = 'medical.request.group'

    can_change_plan = fields.Boolean(
        compute='_compute_can_change_plan'
    )

    @api.depends('state')
    def _compute_can_change_plan(self):
        for record in self:
            record.can_change_plan = (record.state not in [
                'cancelled', 'completed'])

    def _get_authorization_context(self):
        return {
            'default_request_group_id': self.id,
            'default_authorization_number': self.authorization_number
        }

    @api.multi
    def check_authorization_action(self):
        self.ensure_one()
        action = self.env.ref(
            'cb_medical_financial_coverage_request.'
            'medical_request_group_check_authorization_action')
        result = action.read()[0]
        ctx = safe_eval(result['context']) or {}
        ctx.update(self._get_authorization_context())
        result['context'] = ctx
        return result
