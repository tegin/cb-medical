from odoo import fields, models


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    trigger_ids = fields.One2many(
        'medical.request.trigger',
        compute='_compute_triggers',
        string='Elements that will be triggered',
    )
    triggerer_ids = fields.One2many(
        'medical.request.trigger',
        compute='_compute_triggerers',
        string='Elements that will trigger the request',
    )

    def _compute_triggers(self):
        for rec in self:
            rec.trigger_ids = self.env['medical.request.trigger'].search([
                ('trigger_id', '=', rec.id),
                ('trigger_model', '=', rec._name),
            ])

    def _compute_triggerers(self):
        for rec in self:
            rec.triggerer_ids = self.env['medical.request.trigger'].search([
                ('request_id', '=', rec.id),
                ('request_model', '=', rec._name),
            ])
