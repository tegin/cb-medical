from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    cancel_reason_id = fields.Many2one('medical.cancel.reason')

    @api.constrains('state', 'cancel_reason_id')
    def check_cancel_reason_state(self):
        for rec in self:
            if rec.state == 'cancelled' and not rec.cancel_reason_id:
                raise ValidationError(_(
                    'A cancellation reason is required for cancelled requests'
                ))
            if rec.state != 'cancelled' and rec.cancel_reason_id:
                raise ValidationError(_(
                    'A cancellation reason is only allowed on cancelled '
                    'requests'
                ))

    def cancel_values(self):
        vals = super().cancel_values()
        vals.update({
            'cancel_reason_id': self.env.context.get('cancel_reason_id', False)
        })
        return vals

    def _check_cancellable(self):
        return not self.filtered(lambda r: r.state in [
            'completed', 'entered-in-error', 'cancelled'])

    @api.multi
    def check_cancellable(self):
        result = True
        if not self._check_cancellable():
            return False
        models = [self.env[model] for model in self._get_request_models()]
        fieldname = self._get_parent_field_name()
        for model in models:
            childs = model.search([
                (fieldname, 'in', self.ids),
                ('parent_id', 'in', self.ids),
                ('parent_model', '=', self._name),
            ] + model.cancellation_domain())
            if childs:
                result = result and childs.check_cancellable()
        return result

    @api.model
    def cancellation_domain(self):
        return [('state', '!=', 'cancelled')]

    @api.multi
    def cancel(self):
        if not self.check_cancellable():
            raise ValidationError(_('It is not cancelable'))
        models = [self.env[model] for model in self._get_request_models()]
        fieldname = self._get_parent_field_name()
        for model in models:
            childs = model.search([
                (fieldname, 'in', self.ids),
                ('parent_id', 'in', self.ids),
                ('parent_model', '=', self._name),
            ] + model.cancellation_domain())
            if childs:
                childs.with_context(cancel_child=True).cancel()
        res = super().cancel()
        cancel_reason = self.env.context.get('cancel_reason', False)
        if not self.env.context.get('cancel_child', False) and cancel_reason:
            for r in self:
                r.message_post(subtype=False, body=cancel_reason)
        return res
