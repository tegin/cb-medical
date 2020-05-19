# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalAuthorizationMethod(models.Model):

    _inherit = "medical.authorization.method"

    force_item_authorization_method = fields.Boolean()
