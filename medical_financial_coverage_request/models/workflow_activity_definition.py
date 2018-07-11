# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class ActivityDefinition(models.Model):
    _inherit = 'workflow.activity.definition'

    def _get_activity_values(self, vals, parent=False, plan=False, action=False
                             ):
        res = super()._get_activity_values(vals, parent, plan, action)
        if (
            'relations' in res.keys() and
            self.type_id == self.env.ref('medical_workflow.medical_workflow')
        ):
            del res['relations']
        return res

    def _get_medical_values(self, vals, parent=False, plan=False, action=False
                            ):
        res = super()._get_medical_values(vals, parent, plan, action)

        res['coverage_agreement_item_id'] = False
        res['coverage_agreement_id'] = False
        res['authorization_method_id'] = False
        if not res.get('is_billable', False):
            return res
        if vals.get('coverage_id', False):
            coverage_template = self.env['medical.coverage'].browse(vals.get(
                'coverage_id')).coverage_template_id
            cai = self.env['medical.coverage.agreement.item'].search([
                ('coverage_template_ids', '=', coverage_template.id),
                ('product_id', '=', self.service_id.id)
            ], limit=1)
            if not cai:
                raise ValidationError(_(
                    'An element should exist on an agreement if it is billable'
                ))
            res['coverage_agreement_item_id'] = cai.id
            res['coverage_agreement_id'] = cai.coverage_agreement_id.id
            res['authorization_method_id'] = cai.authorization_method_id.id
            if cai.authorization_method_id.always_authorized:
                res['authorization_status'] = 'authorized'
            else:
                res['authorization_status'] = 'pending'
        return res

    @api.multi
    def execute_activity(self, vals, parent=False, plan=False, action=False):
        self.ensure_one()
        if action.id in vals.get('relations', []):
            return self.env[self.model_id.model].browse(
                vals['relations'][action.id])
        return super().execute_activity(vals, parent, plan, action)
