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
        if parent:
            res['parent_model'] = parent._name
            res['parent_id'] = parent.id
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
            vals = cai._check_authorization(cai.authorization_method_id, **res)
            res.update(vals)
        if parent:
            res.update({
                'parent_id': parent.id,
                'parent_model': parent._name,
            })
        return res

    @api.multi
    def execute_activity(self, vals, parent=False, plan=False, action=False):
        self.ensure_one()
        if action.id in vals.get('relations', {}):
            activity = self.env[self.model_id.model].browse(
                vals['relations'][action.id])
            activity._update_related_activity(vals, parent, plan, action)
            return activity
        return super().execute_activity(vals, parent, plan, action)
