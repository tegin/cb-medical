# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class MedicalAuthorizationMethod(models.Model):
    _name = 'medical.authorization.method'
    _description = 'Authorization method'

    code = fields.Char(required=True,)
    name = fields.Char(required=True,)
    method_information = fields.Text()
    vat_required = fields.Boolean(
        track_visibility=True,
        required=True,
        default=False,
    )
    subscriber_id_required = fields.Boolean(
        track_visibility=True,
        required=True,
        default=False,
    )
    subscriber_magnetic_str_required = fields.Boolean(
        track_visibility=True,
        required=True,
        default=False,
    )
    authorization_required = fields.Boolean(
        track_visibility=True,
        required=True,
        default=False,
        oldname='number_required'
    )
    auxiliary_method_id = fields.Many2one(
        comodel_name='medical.authorization.method',
        required=False,
    )
    always_authorized = fields.Boolean(default=False)
    integration_system = fields.Selection([
        ('none', 'None'),
        ('web', 'Web'),
        ('ws', 'Web service')
    ], default='none', required=True, track_visibility=True)
    integration_information = fields.Char()
