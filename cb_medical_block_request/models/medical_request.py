from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    is_blocking = fields.Boolean(default=False, readonly=True)

    @api.model
    def _blocking_states(self):
        return ["draft", "active"]

    def _has_blocking(self):
        fieldname = self._get_parent_field_name()
        request_models = self._get_request_models()
        states = self._blocking_states()
        if self.filtered(lambda r: r.is_blocking and r.fhir_state in states):
            raise ValidationError(_("A request is blocking"))
        for request in self:
            query = [
                (fieldname, "=", request.id),
                ("parent_id", "=", request.id),
                ("parent_model", "=", request._name),
                ("state", "!=", "cancelled"),
            ]
            for model in request_models:
                self.env[model].search(query)._has_blocking()
