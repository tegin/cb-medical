# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class MedicalAuthorizationMethod(models.Model):
    _name = 'medical.authorization.method'
    _description = 'Authorization method'

    code = fields.Char(required=True,)
    name = fields.Char(required=True,)
    number_required = fields.Boolean(
        track_visibility=True,
        required=True,
        default=False,
    )
    auxiliary_method_id = fields.Many2one(
        comodel_name='medical.authorization.method',
        required=False,
    )
    always_authorized = fields.Boolean(default=False)
