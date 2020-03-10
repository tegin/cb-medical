# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalAuthorizationMethod(models.Model):
    _name = "medical.authorization.method"
    _description = "Authorization method"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    description = fields.Char()
    method_information = fields.Text()
    vat_required = fields.Boolean(
        track_visibility=True, required=True, default=False
    )
    subscriber_id_required = fields.Boolean(
        track_visibility=True, required=True, default=False
    )
    subscriber_magnetic_str_required = fields.Boolean(
        track_visibility=True, required=True, default=False
    )
    authorization_required = fields.Boolean(
        track_visibility=True,
        required=True,
        default=False,
        oldname="number_required",
    )
    auxiliary_method_id = fields.Many2one(
        comodel_name="medical.authorization.method", required=False
    )
    always_authorized = fields.Boolean(default=False)
    integration_system = fields.Selection(
        [("none", "None"), ("web", "Web"), ("ws", "Web service")],
        default="none",
        required=True,
        track_visibility=True,
    )
    integration_information = fields.Char()
    authorization_web_id = fields.Many2one(
        'medical.authorization.web',
    )

    def _update_web_method(self, vals):
        authorization_web_id = vals.get('authorization_web_id', False)
        if authorization_web_id:
            authorization_web = self.env['medical.authorization.web'].browse(
                authorization_web_id
            )
            vals.update({
                'integration_information': authorization_web.link,
                'method_information': authorization_web.notes,
            })
            return vals
        return vals

    @api.model
    def create(self, vals):
        return super().create(self._update_web_method(vals))

    def write(self, vals):
        return super().write(self._update_web_method(vals))
