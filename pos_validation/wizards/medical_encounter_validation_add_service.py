# Copyright 2018 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalEncounterValidationAddService(models.TransientModel):
    _name = 'medical.encounter.validation.add.service'
    _inherit = 'medical.careplan.add.plan.definition'

    encounter_id = fields.Many2one(
        'medical.encounter',
        required=True,
    )
    action_type = fields.Selection([
        ('new', 'New Careplan'),
        ('reuse', 'Reuse Careplan')
    ], required=True, default='reuse', )
    careplan_id = fields.Many2one(
        'medical.careplan',
        required=False,
    )
    patient_id = fields.Many2one(
        related='encounter_id.patient_id', readonly=True,
    )
    payor_id = fields.Many2one(
        'res.partner',
        domain=[('is_payor', '=', True)],
    )
    coverage_template_id = fields.Many2one(
        related=False,
        readonly=False,
    )
    sub_payor_id = fields.Many2one(
        'res.partner',
    )
    sub_payor_required = fields.Boolean()
    center_id = fields.Many2one(
        related='encounter_id.center_id', readonly=True,
    )
    subscriber_id = fields.Char()
    is_phantom = fields.Boolean()

    @api.onchange('action_type')
    def _onchange_action_type(self):
        self.careplan_id = False
        self.payor_id = False
        self.coverage_template_id = False
        self.sub_payor_id = False
        self.subscriber_id = False

    @api.onchange('careplan_id')
    def _onchange_careplan(self):
        coverage = self.careplan_id.coverage_id
        self.payor_id = coverage.coverage_template_id.payor_id
        self.sub_payor_id = self.careplan_id.sub_payor_id
        self.coverage_template_id = coverage.coverage_template_id
        self.subscriber_id = coverage.subscriber_id

    @api.onchange('payor_id')
    def _onchange_payor(self):
        if self.action_type != 'new':
            return
        if not self.payor_id:
            self.coverage_template_id = False
            self.sub_payor_id = False
            self.subscriber_id = False
            return
        sub_payors = self.payor_id.sub_payor_ids
        self.sub_payor_required = bool(sub_payors)
        if len(sub_payors) == 1:
            self.sub_payor_id = sub_payors
        if len(self.payor_id.coverage_template_ids) == 1:
            self.coverage_template_id = self.payor_id.coverage_template_ids
        return {"domain": {"coverage_template_id": [
            ("payor_id", "=", self.payor_id.id or False)
        ]}}

    def post_process_request(self, request):
        pass

    def create_careplan(self):
        wizard = self.env[
            'medical.encounter.add.careplan'
        ].with_context(
            on_validation=True,
        ).create({
            'patient_id': self.patient_id.id,
            'encounter_id': self.encounter_id.id,
            'center_id': self.encounter_id.center_id.id,
            'coverage_template_id': self.coverage_template_id.id,
            'payor_id': self.payor_id.id,
            'sub_payor_id': self.sub_payor_id.id or False,
            'subscriber_id': self.subscriber_id,
        })
        return wizard.run()

    def run(self):
        if self.action_type == 'new':
            self.careplan_id = self.create_careplan()
        res = super(MedicalEncounterValidationAddService, self.with_context(
            on_validation=True
        ))._run()
        values = dict()
        self.post_process_request(res)
        query = res.get_sale_order_query()
        for el in query:
            key, partner, cov, is_ins, third_party, request = el
            if not values.get(key, False):
                values[key] = {}
            if not values[key].get(partner, False):
                values[key][partner] = {}
            if not values[key][partner].get(cov, False):
                values[key][partner][cov] = {}
            if not values[key][partner][cov].get(third_party, False):
                values[key][partner][cov][third_party] = []
            values[key][partner][cov][third_party].append(
                request.get_sale_order_line_vals(is_ins))
        self.encounter_id.generate_sale_orders(values)
        return
