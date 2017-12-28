# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, _
from odoo.exceptions import ValidationError


class ActivityDefinition(models.Model):
    _inherit = 'workflow.activity.definition'

    def _get_medical_values(self, vals, parent=False, plan=False, action=False
                            ):
        res = super(ActivityDefinition, self)._get_medical_values(
            vals, parent, plan, action)
        res['coverage_agreement_item_id'] = False
        res['coverage_agreement_id'] = False
        if vals.get('coverage_id', False):
            coverage_template = self.env['medical.coverage'].browse(vals.get(
                'coverage_id')).coverage_template_id
            cai = self.env['medical.coverage.agreement.item'].search([
                ('coverage_template_ids', '=', coverage_template.id),
                ('product_id', '=', self.service_id.id)
            ], limit=1)
            if res.get('is_billable', False) and not cai:
                raise ValidationError(_(
                    'An element should exist on an agreement if it is billable'
                ))
            if cai:
                res['coverage_agreement_item_id'] = cai.id
                res['coverage_agreement_id'] = cai.coverage_agreement_id.id
        return res
