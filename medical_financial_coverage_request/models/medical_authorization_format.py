# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import re

from odoo import fields, models


class MedicalAuthorizationFormat(models.Model):
    _name = "medical.authorization.format"
    _description = "Authorization format"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(default=True)
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    authorization_format = fields.Char(tracking=True)
    authorization_information = fields.Text()
    always_authorized = fields.Boolean(default=False, tracking=True, required=True)
    requires_authorization_extra_1 = fields.Boolean()
    authorization_extra_1_format = fields.Char(tracking=True)
    authorization_extra_1_information = fields.Text()

    def check_value(
        self,
        authorization_number,
        authorization_number_extra_1=False,
        ignore_extra=False,
    ):
        if self.always_authorized:
            return True
        if not self._check_value(authorization_number, "authorization"):
            return False
        if ignore_extra:
            return True
        if self.requires_authorization_extra_1:
            return self._check_value(
                authorization_number_extra_1, "authorization_extra_1"
            )
        return True

    def _check_value(self, value, field):
        if not value:
            return False
        match = re.match(self["%s_format" % field], value)
        if match:
            return True
        return False
