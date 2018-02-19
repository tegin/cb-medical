# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import re
from odoo import models, fields


class MedicalAuthorizationFormat(models.Model):
    _name = 'medical.authorization.format'
    _description = 'Authorization format'

    code = fields.Char(required=True,)
    name = fields.Char(required=True,)
    formula = fields.Char(required=True,)
    authorization_information = fields.Text()

    def check_value(self, value):
        match = re.match(self.formula, value)
        if match:
            return True
        return False
