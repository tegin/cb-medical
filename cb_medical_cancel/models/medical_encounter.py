from odoo import api, models, _
from odoo.exceptions import ValidationError


class MedicalEncounter(models.AbstractModel):
    _inherit = 'medical.encounter'

    @api.multi
    def cancel(self, cancel_reason_id, session, cancel_reason=False):
        self.ensure_one()
        models = [self.env[model] for model in
                  self.env['medical.request']._get_request_models()]
        states = ['onleave', 'completed', 'entered-in-error', 'cancelled']
        if self.state in states:
            raise ValidationError(_(
                "Encounter %s can't be cancelled" % self.display_name
            ))
        for model in models:
            childs = model.search([
                ('encounter_id', '=', self.id),
                ('parent_id', '=', False),
                ('parent_model', '=', False),
                ('state', '!=', 'cancelled')
            ])
            childs.with_context({
                'cancel_reason_id': cancel_reason_id.id,
                'cancel_reason': cancel_reason
            }).cancel()
        self.with_context(
            pos_session_id=session.id,
            company_id=session.config_id.company_id.id
        ).inprogress2onleave()
        if cancel_reason:
            self.message_post(subtype=False, body=cancel_reason)
