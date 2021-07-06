# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import re

from odoo import fields, models


class MedicalAuthorizationFormat(models.Model):
    _name = "medical.authorization.format"
    _description = "Authorization format"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    authorization_format = fields.Char(tracking=True)
    authorization_information = fields.Text()
    always_authorized = fields.Boolean(
        default=False, tracking=True, required=True
    )

    def check_value(self, value):
        if self.always_authorized:
            return True
        if not value:
            return False
        match = re.match(self.authorization_format, value)
        if match:
            return True
        return False
