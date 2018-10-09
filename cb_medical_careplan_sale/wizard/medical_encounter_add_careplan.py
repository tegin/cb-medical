# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalEncounterAddCareplan(models.TransientModel):
    _name = 'medical.encounter.add.careplan'

    @api.model
    def get_encounter_states(self):
        return ['arrived', 'in-progress', 'on-leave']

    @api.model
    def get_careplan_states(self):
        return ['draft', 'active']

    @api.model
    def default_center(self):
        if self._context.get('default_encounter_id', False):
            return self.env['medical.encounter'].browse(
                self._context.get('default_encounter_id', False)
            ).center_id

    encounter_id = fields.Many2one(
        'medical.encounter',
        required=True,
        readonly=True,
        domain=[('state', 'in', get_encounter_states)]
    )
    patient_id = fields.Many2one(
        'medical.patient',
        related='encounter_id.patient_id',
    )
    center_id = fields.Many2one(
        'res.partner',
        default=default_center,
        required=True,
        domain=[('is_center', '=', True)]
    )
    payor_id = fields.Many2one(
        'res.partner',
        required=True,
        domain="[('is_payor', '=', True)]",
    )
    sub_payor_id = fields.Many2one(
        'res.partner',
        domain="[('payor_id', '=', payor_id), ('is_sub_payor', '=', True)]",
    )
    coverage_id = fields.Many2one(
        'medical.coverage',
        domain="[('patient_id','=', patient_id)]",
    )
    coverage_template_id = fields.Many2one(
        'medical.coverage.template',
        required=True,
        domain="[('payor_id', '=', payor_id)]",
    )
    subscriber_magnetic_str = fields.Char()
    subscriber_id = fields.Char()

    def get_careplan_values(self):
        return {
            'patient_id': self.patient_id.id,
            'encounter_id': self.encounter_id.id,
            'center_id': self.center_id.id,
            'coverage_id': self.patient_id.get_coverage(
                template=self.coverage_template_id,
                coverage=self.coverage_id,
                subscriber_id=self.subscriber_id,
                magnetic_str=self.subscriber_magnetic_str,
            ).id,
            'sub_payor_id': self.sub_payor_id.id
        }

    @api.onchange('payor_id')
    def onchange_payor(self):
        if self.payor_id:
            if self.coverage_template_id.payor_id != self.payor_id:
                self.coverage_template_id = False
            if self.sub_payor_id.payor_id != self.payor_id:
                self.sub_payor_id = False

    @api.onchange('coverage_template_id')
    def onchange_coverage_template(self):
        if self.coverage_template_id:
            if (
                        self.coverage_template_id !=
                        self.coverage_id.coverage_template_id
            ):
                self.coverage_id = False
                self.subscriber_id = False
                self.subscriber_magnetic_str = False

    @api.onchange('coverage_id')
    def onchange_coverage(self):
        if self.coverage_id:
            self.payor_id = self.coverage_id.coverage_template_id.payor_id
            self.coverage_template_id = self.coverage_id.coverage_template_id
            self.subscriber_id = self.coverage_id.subscriber_id
            self.subscriber_magnetic_str = (
                self.coverage_id.subscriber_magnetic_str
            )

    @api.multi
    def run(self):
        self.ensure_one()
        if self.encounter_id.state not in self.get_encounter_states():
            raise ValidationError(_(
                'Encounter is not valid'
            ))
        vals = self.get_careplan_values()
        cp = self.encounter_id.careplan_ids.filtered(
            lambda r: (
                r.coverage_id.id == vals.get('coverage_id', False) and
                ((
                    r.sub_payor_id
                    and r.sub_payor_id.id == vals.get('sub_payor_id', False)
                ) or (
                    not r.sub_payor_id and not vals.get('sub_payor_id', False)
                )) and
                r.state in self.get_careplan_states()
            )
        )
        if cp:
            return cp[0]
        return self.env['medical.careplan'].create(vals)
