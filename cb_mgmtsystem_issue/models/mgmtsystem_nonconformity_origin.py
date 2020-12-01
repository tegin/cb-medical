# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemNonconformityOrigin(models.Model):

    _inherit = "mgmtsystem.nonconformity.origin"

    notify_creator = fields.Boolean(string="Notify Creator")
