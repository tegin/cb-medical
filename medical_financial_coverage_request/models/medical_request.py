# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    coverage_id = fields.Many2one(
        'medical.coverage',
        track_visibility=True,
        required=False,
        domain="[('patient_id', '=', patient_id)]"
    )
    coverage_agreement_item_id = fields.Many2one(
        'medical.coverage.agreement.item',
        readonly=True,
        ondelete='restrict'
    )
    coverage_agreement_id = fields.Many2one(
        'medical.coverage.agreement',
        readonly=True,
        ondelete='restrict'
    )
    authorization_method_id = fields.Many2one(
        comodel_name='medical.authorization.method'
    )
    authorization_number = fields.Char(
        track_visibility=True,
    )
    authorization_status = fields.Selection([
        ('pending', 'Pending authorization'),
        ('not-authorized', 'Not authorized'),
        ('authorized', 'Authorized'),
    ], readonly=True,)
    can_deactivate = fields.Boolean(
        compute='_compute_can_deactivate'
    )

    @api.depends('state')
    def _compute_can_deactivate(self):
        for record in self:
            record.can_deactivate = (record.state == 'draft')

    def update_plan_vals(self, relations):
        return {
            'patient_id': self.patient_id.id,
            'careplan_id': self.careplan_id.id or False,
            'center_id': self.center_id.id or False,
            'relations': relations,
            'coverage_id': self.coverage_id.id,
            'coverage_agreement_item_id': self.coverage_agreement_item_id.id,
            'authorization_method_id': self.authorization_method_id.id,
            'authorization_number': self.authorization_number,
            'coverage_agreement_id': self.coverage_agreement_id.id,
        }

    def update_plan_definition(self, plan, coverage_agreement_item_id):
        self.plan_definition_id = plan
        self.is_billable = plan.is_billable
        self.is_breakdown = plan.is_breakdown
        self.coverage_agreement_item_id = coverage_agreement_item_id
        self.coverage_agreement_id = \
            coverage_agreement_item_id.coverage_agreement_id
        self.service_id = coverage_agreement_item_id.product_id
        self.name = coverage_agreement_item_id.product_id.name

    def check_plan_definition_change(self, plan):
        relations = {}
        activities = {}
        for action in plan.action_ids:
            if not activities.get(action.activity_definition_id.id, False):
                activities[action.activity_definition_id.id] = []
            activities[action.activity_definition_id.id].append(action.id)
        for model in self._get_request_models():
            for child in self.env[model].search([
                (self._get_parent_field_name(), '=', self.id),
                ('active', '=', True)
            ]):
                if child.can_deactivate:
                    child.toggle_active()
                elif child.activity_definition_id.id in activities:
                    action = activities[child.activity_definition_id.id].pop()
                    relations[action] = child.id
                    if len(activities[child.activity_definition_id.id]) == 0:
                        del activities[child.activity_definition_id.id]
                else:
                    raise ValidationError(_(
                        'Plans cannot be interchanged'
                    ))
        return relations

    def change_plan_definition(self, coverage_agreement_item_id):
        self.ensure_one()
        plan = coverage_agreement_item_id.plan_definition_id
        if not self.active:
            raise ValidationError(_(
                'Element is inactive, your cannot change plan'
            ))
        if self.plan_definition_id == plan:
            self.update_plan_definition(plan, coverage_agreement_item_id)
            return
        if self.plan_definition_action_id:
            raise ValidationError(_(
                'A change of plan definition must be made on headers'
            ))
        relations = self.check_plan_definition_change(plan)
        self.update_plan_definition(plan, coverage_agreement_item_id)
        self.plan_definition_id.execute_plan_definition(
            self.update_plan_vals(relations), self
        )
